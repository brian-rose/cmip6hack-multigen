import xarray as xr

from.np_deterministic import _pearson_r, _pearson_r_p_value, _rmse, _mse, _mae


__all__ = ['pearson_r', 'pearson_r_p_value', 'rmse', 'mse', 'mae']


def _preprocess_dims(dim):
    """Preprocesses dimensions to prep for stacking.
    
    Parameters
    ----------
    dim : str, list
        The dimension(s) to apply the function along.
    """
    if isinstance(dim, str):
        dim = [dim]
    axis = tuple(range(-1, -len(dim) - 1, -1))
    return dim, axis


def _preprocess_weights(a, dim, new_dim, weights):
    """Preprocesses weights array to prepare for numpy computation.
    
    Parameters
    ----------
    a : Dataset, DataArray, GroupBy, Variable, numpy/dask arrays or scalars
        One of the arrays over which the function will be applied.
    dim : str, list
        The original dimension(s) to apply the function along.
    new_dim : str
        The newly named dimension after running ``_preprocess_dims``
    weights : Dataset, DataArray, GroupBy, Variable, numpy/dask arrays or scalars
        Weights to apply to function, matching the dimension size of ``new_dim``.
    """
    if weights is None:
        weights = xr.ones_like(a)  # Evenly weight
    else:
        # Scale weights to vary from 0 to 1.
        weights = weights / weights.max()
        # Throw error if there are negative weights.
        if weights.min() < 0:
            raise ValueError(
                f"Weights has a minimum below 0. Please submit a weights array "
                f"of positive numbers."
                )
        # Check that the weights array has the same size
        # dimension(s) as those being applied over.
        drop_dims = [i for i in a.dims if i not in new_dim]
        drop_dims = {k: 0 for k in drop_dims}
        if dict(weights.sizes) != dict(a.isel(drop_dims).sizes):
            raise ValueError(
                f"weights dimension(s) {dim} of size {dict(weights.sizes)} "
                f"does not match DataArray's size {dict(a.isel(drop_dims).sizes)}"
                )
        if dict(weights.sizes) != dict(a.sizes):
            # Broadcast weights to full size of main object.
            _, weights = xr.broadcast(a, weights)
    return weights


def pearson_r(a, b, dim, weights=None):
    """
    Pearson's correlation coefficient.

    Parameters
    ----------
    a : Dataset, DataArray, GroupBy, Variable, numpy/dask arrays or scalars
        Mix of labeled and/or unlabeled arrays to which to apply the function.
    b : Dataset, DataArray, GroupBy, Variable, numpy/dask arrays or scalars
        Mix of labeled and/or unlabeled arrays to which to apply the function.
    dim : str, list
        The dimension(s) to apply the correlation along.
    weights : Dataset, DataArray, GroupBy, Variable, numpy/dask arrays or scalars
        Weights matching dimensions of ``dim`` to apply during the function.
        If None, an array of ones will be applied (i.e., no weighting).

    Returns
    -------
    Single value or tuple of Dataset, DataArray, Variable, dask.array.Array or
    numpy.ndarray, the first type on that list to appear on an input.
        Pearson's correlation coefficient.

    See Also
    --------
    scipy.stats.pearsonr
    xarray.apply_ufunc

    """
    dim, _ = _preprocess_dims(dim)
    if len(dim) > 1:
        new_dim = '_'.join(dim)
        a = a.stack(**{new_dim: dim})
        b = b.stack(**{new_dim: dim})
        if weights is not None:
            weights = weights.stack(**{new_dim: dim})
    else:
        new_dim = dim[0]
    weights = _preprocess_weights(a, dim, new_dim, weights)


    return xr.apply_ufunc(_pearson_r, a, b, weights,
                          input_core_dims=[[new_dim], [new_dim], [new_dim]],
                          kwargs={'axis': -1},
                          dask='parallelized',
                          output_dtypes=[float])


def pearson_r_p_value(a, b, dim, weights=None):
    """
    2-tailed p-value associated with pearson's correlation coefficient.

    Parameters
    ----------
    a : Dataset, DataArray, GroupBy, Variable, numpy/dask arrays or scalars
        Mix of labeled and/or unlabeled arrays to which to apply the function.
    b : Dataset, DataArray, GroupBy, Variable, numpy/dask arrays or scalars
        Mix of labeled and/or unlabeled arrays to which to apply the function.
    dim : str, list
        The dimension(s) to apply the correlation along.
    weights : Dataset, DataArray, GroupBy, Variable, numpy/dask arrays or scalars
        Weights matching dimensions of ``dim`` to apply during the function.
        If None, an array of ones will be applied (i.e., no weighting).

    Returns
    -------
    Single value or tuple of Dataset, DataArray, Variable, dask.array.Array or
    numpy.ndarray, the first type on that list to appear on an input.
        2-tailed p-value.

    See Also
    --------
    scipy.stats.pearsonr
    xarray.apply_ufunc

    """
    dim, _ = _preprocess_dims(dim)
    if len(dim) > 1:
        new_dim = '_'.join(dim)
        a = a.stack(**{new_dim: dim})
        b = b.stack(**{new_dim: dim})
        if weights is not None:
            weights = weights.stack(**{new_dim: dim})
    else:
        new_dim = dim[0]
    weights = _preprocess_weights(a, dim, new_dim, weights)

    return xr.apply_ufunc(_pearson_r_p_value, a, b, weights,
                          input_core_dims=[[new_dim], [new_dim], [new_dim]],
                          kwargs={'axis': -1},
                          dask='parallelized',
                          output_dtypes=[float])


def rmse(a, b, dim, weights=None):
    """
    Root Mean Squared Error.

    Parameters
    ----------
    a : Dataset, DataArray, GroupBy, Variable, numpy/dask arrays or scalars
        Mix of labeled and/or unlabeled arrays to which to apply the function.
    b : Dataset, DataArray, GroupBy, Variable, numpy/dask arrays or scalars
        Mix of labeled and/or unlabeled arrays to which to apply the function.
    dim : str, list
        The dimension(s) to apply the rmse along.
    weights : Dataset, DataArray, GroupBy, Variable, numpy/dask arrays or scalars
        Weights matching dimensions of ``dim`` to apply during the function.
        If None, an array of ones will be applied (i.e., no weighting).

    Returns
    -------
    Single value or tuple of Dataset, DataArray, Variable, dask.array.Array or
    numpy.ndarray, the first type on that list to appear on an input.
        Root Mean Squared Error.

    See Also
    --------
    sklearn.metrics.mean_squared_error
    xarray.apply_ufunc

    """
    dim, axis = _preprocess_dims(dim)
    weights = _preprocess_weights(a, dim, dim, weights)

    return xr.apply_ufunc(_rmse, a, b, weights,
                          input_core_dims=[dim, dim, dim],
                          kwargs={'axis': axis},
                          dask='parallelized',
                          output_dtypes=[float])


def mse(a, b, dim, weights=None):
    """
    Mean Squared Error.

    Parameters
    ----------
    a : Dataset, DataArray, GroupBy, Variable, numpy/dask arrays or scalars
        Mix of labeled and/or unlabeled arrays to which to apply the function.
    b : Dataset, DataArray, GroupBy, Variable, numpy/dask arrays or scalars
        Mix of labeled and/or unlabeled arrays to which to apply the function.
    dim : str, list
        The dimension(s) to apply the mse along.
    weights : Dataset, DataArray, GroupBy, Variable, numpy/dask arrays or scalars
        Weights matching dimensions of ``dim`` to apply during the function.
        If None, an array of ones will be applied (i.e., no weighting).

    Returns
    -------
    Single value or tuple of Dataset, DataArray, Variable, dask.array.Array or
    numpy.ndarray, the first type on that list to appear on an input.
        Mean Squared Error.

    See Also
    --------
    sklearn.metrics.mean_squared_error
    xarray.apply_ufunc

    """
    dim, axis = _preprocess_dims(dim)
    weights = _preprocess_weights(a, dim, dim, weights)

    return xr.apply_ufunc(_mse, a, b, weights,
                          input_core_dims=[dim, dim, dim],
                          kwargs={'axis': axis},
                          dask='parallelized',
                          output_dtypes=[float])


def mae(a, b, dim, weights=None):
    """
    Mean Absolute Error.

    Parameters
    ----------
    a : Dataset, DataArray, GroupBy, Variable, numpy/dask arrays or scalars
        Mix of labeled and/or unlabeled arrays to which to apply the function.
    b : Dataset, DataArray, GroupBy, Variable, numpy/dask arrays or scalars
        Mix of labeled and/or unlabeled arrays to which to apply the function.
    dim : str, list
        The dimension(s) to apply the mae along.
    weights : Dataset, DataArray, GroupBy, Variable, numpy/dask arrays or scalars
        Weights matching dimensions of ``dim`` to apply during the function.
        If None, an array of ones will be applied (i.e., no weighting).

    Returns
    -------
    Single value or tuple of Dataset, DataArray, Variable, dask.array.Array or
    numpy.ndarray, the first type on that list to appear on an input.
        Mean Absolute Error.

    See Also
    --------
    sklearn.metrics.mean_absolute_error
    xarray.apply_ufunc

    """
    dim, axis = _preprocess_dims(dim)
    weights = _preprocess_weights(a, dim, dim, weights)

    return xr.apply_ufunc(_mae, a, b, weights,
                          input_core_dims=[dim, dim, dim],
                          kwargs={'axis': axis},
                          dask='parallelized',
                          output_dtypes=[float])
