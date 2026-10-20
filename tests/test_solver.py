import numpy as np
import pytest

from radiation import Geometry, calculate_view_factors, solve_radiation


def test_closed_eccentric_enclosure_has_reciprocal_nonnegative_view_factors():
    model = calculate_view_factors(Geometry(r=0.4, d=0.3, n_outer=12, n_inner=8))
    assert np.min(model.factors) >= 0
    np.testing.assert_allclose(model.factors.sum(axis=1), 1, atol=1e-12)
    exchange = model.areas[:, None] * model.factors
    np.testing.assert_allclose(exchange, exchange.T, atol=2e-7)
    np.testing.assert_array_equal(model.factors[12:, 12:], 0)


def test_equal_temperatures_produce_no_net_heat_flux():
    model = calculate_view_factors(Geometry(n_outer=8, n_inner=8))
    result = solve_radiation(model, temperature_outer_k=350, temperature_inner_k=350,
                             emissivity_outer=0.6, emissivity_inner=0.8)
    np.testing.assert_allclose(result.flux, 0, atol=1e-9)


def test_outer_wall_cannot_see_through_inner_cylinder():
    model = calculate_view_factors(Geometry(r=0.5, d=0.1, n_outer=24, n_inner=8))
    assert model.factors[0, 12] == 0
    assert model.factors[0, 0] > 0  # a concave arc can see itself


def test_eccentric_gray_enclosure_conserves_heat_and_has_nonuniform_inner_flux():
    model = calculate_view_factors(Geometry(r=0.4, d=0.3, n_outer=12, n_inner=8))
    result = solve_radiation(model)
    assert result.metrics["heat_inner_w_m"] > 0
    assert result.metrics["heat_outer_w_m"] < 0
    assert result.metrics["energy_imbalance_relative"] < 2e-7
    assert result.metrics["max_deviation_percent"] > 0.1


def test_moving_to_the_opposite_side_mirrors_view_factors_and_surface_flux():
    right = calculate_view_factors(Geometry(r=0.4, d=0.3, n_outer=12, n_inner=8))
    left = calculate_view_factors(Geometry(r=0.4, d=0.3, n_outer=12, n_inner=8, side="left"))
    assert left.geometry.center_x == -right.geometry.center_x
    # Reflection across the y-axis maps theta to pi-theta, for both surfaces.
    outer = (6-np.arange(12)-1) % 12
    inner = (4-np.arange(8)-1) % 8
    permutation = np.concatenate([outer, 12+inner])
    np.testing.assert_allclose(left.factors[np.ix_(permutation, permutation)], right.factors, atol=2e-7)
    q_right, q_left = solve_radiation(right), solve_radiation(left)
    np.testing.assert_allclose(q_left.inner_flux[inner], q_right.inner_flux, rtol=2e-7)
    assert q_left.metrics["energy_imbalance_relative"] < 2e-7
    assert q_left.metrics["mean_inner_flux_w_m2"] == pytest.approx(q_right.metrics["mean_inner_flux_w_m2"], rel=2e-7)
    assert q_left.metrics["max_deviation_percent"] == pytest.approx(q_right.metrics["max_deviation_percent"], rel=2e-6)


@pytest.mark.parametrize("options", [{"r": 1}, {"d": 0.7}, {"d": -0.1},
                                     {"n_inner": 3}, {"n_outer": 8.5}, {"r": np.nan}, {"side": "up"}])
def test_invalid_geometry_is_rejected(options):
    with pytest.raises(ValueError):
        Geometry(**options)


@pytest.mark.parametrize("options", [{"temperature_inner_k": 0},
                                     {"emissivity_outer": 0}, {"emissivity_inner": 1.1}])
def test_invalid_thermal_parameters_are_rejected(options):
    model = calculate_view_factors(Geometry(n_outer=4, n_inner=4), 1e-6)
    with pytest.raises(ValueError):
        solve_radiation(model, **options)
