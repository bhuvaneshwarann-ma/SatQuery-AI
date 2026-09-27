"""Bounded TIFF decoding, explicit band selection and reproducible display mapping."""
from pathlib import Path
import numpy as np
import tifffile
from PIL import Image
from ..config import MAX_IMAGE_PIXELS


def read_raster(path):
    with tifffile.TiffFile(path) as raster:
        series = raster.series[0]
        shape, axes = series.shape, series.axes
        if len(shape) not in (2, 3) or 'Y' not in axes or 'X' not in axes:
            raise ValueError(f"Unsupported TIFF axes {axes}; supply a single raster with Y/X axes.")
        h, w = shape[axes.index('Y')], shape[axes.index('X')]
        band_count = int(np.prod(shape) // (h * w))
        if h * w > MAX_IMAGE_PIXELS or band_count > 16:
            raise ValueError("Raster exceeds 4 million pixels or 16 bands; crop or tile it first.")
        if np.prod(shape) * np.dtype(series.dtype).itemsize > 256 * 1024 * 1024:
            raise ValueError("Decoded raster exceeds 256 MiB.")
        arr = series.asarray()
        nodata_tag = raster.pages[0].tags.get(42113)
        nodata = float(nodata_tag.value) if nodata_tag else None
        if arr.ndim == 2:
            arr = arr[..., None]
        else:
            band_axis = next(i for i, axis in enumerate(axes) if axis not in 'YX')
            arr = np.transpose(arr, (axes.index('Y'), axes.index('X'), band_axis))
    return arr, nodata


def render_raster(path, output, bands=None, modality="optical"):
    arr, nodata = read_raster(path)
    count = arr.shape[-1]
    if bands is None:
        if count > 3:
            raise ValueError("Multispectral TIFF requires three zero-based RGB band indices in input_metadata.")
        bands = [0, 0, 0] if modality == "sar" or count < 3 else [0, 1, 2]
    if not isinstance(bands, list) or len(bands) != 3 or any(type(b) is not int or not 0 <= b < count for b in bands):
        raise ValueError("Band mapping must contain three valid zero-based integer indices.")
    channels, stretches = [], []
    for band in bands:
        values = arr[..., band].astype(np.float32)
        valid = np.isfinite(values)
        if nodata is not None:
            valid &= values != nodata
        if not valid.any():
            raise ValueError(f"Band {band} contains no valid pixels.")
        lo, hi = np.percentile(values[valid], [2, 98])
        mapped = np.zeros(values.shape, dtype=np.uint8)
        if hi > lo:
            mapped[valid] = (np.clip((values[valid] - lo) / (hi - lo), 0, 1) * 255).astype(np.uint8)
        channels.append(mapped)
        stretches.append({"band": band, "low": float(lo), "high": float(hi), "valid_pixels": int(valid.sum())})
    Image.fromarray(np.stack(channels, -1)).save(output, "PNG")
    return {"source_format": "TIFF", "source_bands": count, "rgb_bands": bands,
            "modality": modality, "nodata": nodata if nodata is not None and np.isfinite(nodata) else None,
            "display_stretch": stretches, "physical_calibration": "not inferred"}
