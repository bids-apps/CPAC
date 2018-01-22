from unittest import TestCase
from cpac_container_run import *


class TestContainerUtils(TestCase):

    def test_check_download_singularity_image_fail_bad_dir(self):
        self.assertRaises(OSError, check_download_singularity_image, 'bids_cpac_latest.img',
                          '/tmp/singularity_images','s3://fcp-indi/resources')


