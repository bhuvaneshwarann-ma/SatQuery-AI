"""
SatQuery AI — Unit Tests for Geospatial Validation & Raster Compatibility (Phase 8 & 14)
Verifies:
1. Valid PNG / JPEG inspection
2. GeoTIFF / TIFF tag extraction
3. Spatial dimension equality enforcement
4. CRS mismatch rejection with actionable error messages
5. Geographic bounding box overlap verification
6. Non-destructive preview rendering
"""

import os
import sys
import unittest
import numpy as np
from PIL import Image

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from backend.app.services.geospatial_service import (
    extract_raster_metadata,
    validate_pair_compatibility,
    generate_raster_preview,
    GeospatialValidationError,
)


class TestGeospatialValidation(unittest.TestCase):

    def setUp(self):
        self.tmp_dir = "training/data/tmp_test_geo"
        os.makedirs(self.tmp_dir, exist_ok=True)
        self.sample_port = "data/samples/sample_satellite_port.jpg"
        self.sample_t2 = "data/samples/sample_satellite_port_t2_synthetic.jpg"
        self.sample_sar = "data/samples/sample_satellite_port_proxy_sar.png"

        # Create a test GeoTIFF with CRS metadata
        self.test_tif_1 = os.path.join(self.tmp_dir, "test_raster_epsg32643.tif")
        self.test_tif_2 = os.path.join(self.tmp_dir, "test_raster_epsg32644.tif")
        self.test_tif_mismatch_dim = os.path.join(self.tmp_dir, "test_mismatch_dim.tif")

        # Create 100x100 dummy rasters
        arr1 = (np.random.rand(100, 100, 3) * 255).astype(np.uint8)
        img1 = Image.fromarray(arr1)
        # GeoKeyDirectory for EPSG:32643: [1, 1, 0, 1, 3072, 0, 1, 32643]
        img1.save(
            self.test_tif_1,
            tiffinfo={
                33550: (10.0, 10.0, 0.0), # PixelScale
                33922: (0.0, 0.0, 0.0, 500000.0, 2000000.0, 0.0), # Tiepoint
                34735: (1, 1, 0, 1, 3072, 0, 1, 32643), # EPSG:32643
            }
        )

        img2 = Image.fromarray(arr1)
        # GeoKeyDirectory for EPSG:32644 (different UTM zone)
        img2.save(
            self.test_tif_2,
            tiffinfo={
                33550: (10.0, 10.0, 0.0),
                33922: (0.0, 0.0, 0.0, 500000.0, 2000000.0, 0.0),
                34735: (1, 1, 0, 1, 3072, 0, 1, 32644), # EPSG:32644
            }
        )

        arr_dim = (np.random.rand(80, 80, 3) * 255).astype(np.uint8)
        Image.fromarray(arr_dim).save(self.test_tif_mismatch_dim)

    def tearDown(self):
        for f in [self.test_tif_1, self.test_tif_2, self.test_tif_mismatch_dim]:
            if os.path.exists(f):
                try:
                    os.remove(f)
                except Exception:
                    pass

    # Test 1: Standard Image Metadata Extraction
    def test_01_standard_image_metadata(self):
        meta = extract_raster_metadata(self.sample_port)
        self.assertEqual(meta["format"], "JPEG")
        self.assertEqual(meta["width"], 720)
        self.assertEqual(meta["height"], 480)
        self.assertEqual(meta["bands"], 3)
        self.assertFalse(meta["is_geotiff"])

    # Test 2: GeoTIFF Metadata & CRS Parsing
    def test_02_geotiff_metadata_parsing(self):
        meta = extract_raster_metadata(self.test_tif_1)
        self.assertEqual(meta["format"], "GeoTIFF")
        self.assertEqual(meta["width"], 100)
        self.assertEqual(meta["height"], 100)
        self.assertTrue(meta["is_geotiff"])
        self.assertEqual(meta["epsg"], 32643)
        self.assertIn("EPSG:32643", meta["crs"])
        self.assertIsNotNone(meta["bounds"])

    # Test 3: Valid Co-registered Temporal Pair
    def test_03_valid_temporal_pair_compatibility(self):
        compat = validate_pair_compatibility(
            self.sample_port,
            self.sample_t2,
            task_name="CHANGE_DETECTION"
        )
        self.assertEqual(compat["status"], "COMPATIBLE")
        self.assertTrue(compat["co_registered"])
        self.assertEqual(compat["spatial_overlap_percentage"], 100.0)

    # Test 4: Incompatible Spatial Dimensions Rejection
    def test_04_dimension_mismatch_rejection(self):
        with self.assertRaises(GeospatialValidationError) as ctx:
            validate_pair_compatibility(
                self.test_tif_1,
                self.test_tif_mismatch_dim,
                task_name="CHANGE_DETECTION"
            )
        self.assertEqual(ctx.exception.error_code, "DIMENSION_MISMATCH")
        self.assertIn("dimension mismatch", ctx.exception.message.lower())

    # Test 5: Incompatible CRS Rejection
    def test_05_crs_mismatch_rejection(self):
        with self.assertRaises(GeospatialValidationError) as ctx:
            validate_pair_compatibility(
                self.test_tif_1,
                self.test_tif_2,
                task_name="CHANGE_DETECTION"
            )
        self.assertEqual(ctx.exception.error_code, "CRS_MISMATCH")
        self.assertIn("reproject", ctx.exception.message.lower())

    # Test 6: Non-Destructive Preview Generation
    def test_06_preview_generation(self):
        preview_out = os.path.join(self.tmp_dir, "preview.jpg")
        res = generate_raster_preview(self.test_tif_1, preview_out)
        self.assertTrue(os.path.exists(res))
        with Image.open(res) as img:
            self.assertEqual(img.size, (100, 100))


if __name__ == "__main__":
    unittest.main()
