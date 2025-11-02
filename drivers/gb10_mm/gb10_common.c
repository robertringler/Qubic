// SPDX-License-Identifier: Apache-2.0
#include "../include/gb10_drv_common.h"
#include <linux/kernel.h>
#include <linux/slab.h>

int gb10_register_device(struct device *dev, const char *name) {
  dev_info(dev, "GB10 device %s registered\n", name);
  return 0;
}

void gb10_unregister_device(struct device *dev, const char *name) {
  dev_info(dev, "GB10 device %s unregistered\n", name);
}
