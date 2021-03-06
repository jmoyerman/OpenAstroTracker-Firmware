import os
import itertools
from collections import defaultdict
import time

CONTINUE_ON_ERROR = True

platforms = {
    "0001": "mega2560",
    "1001": "esp32"
}

matrix = {
    "PLATFORM": ['0001', '1001'],
    "BOARD": ['0001', '0002', '0003', '0004', '1001'],
    "RA_STEPPER_TYPE": [0, 1],
    "DEC_STEPPER_TYPE": [0, 1],
    "RA_DRIVER_TYPE": [0, 1, 2, 3],
    "DEC_DRIVER_TYPE": [0, 1, 2, 3],
    "USE_GPS": [0, 1],
    "USE_GYRO_LEVEL": [0, 1],
    "AZIMUTH_ALTITUDE_MOTORS": [0, 1],
    #"AZ_STEPPER_TYPE": [0, 1],
    #"ALT_STEPPER_TYPE": [0, 1],
    #"AZ_DRIVER_TYPE": [0, 1, 2, 3],
    #"ALT_DRIVER_TYPE": [0, 1, 2, 3],
    "DISPLAY_TYPE": [0, 1],
}

# forbidden combinations
filters = [
    # not possible combinations
    {'RA_STEPPER_TYPE': 0, 'RA_DRIVER_TYPE': 1},
    {'DEC_STEPPER_TYPE': 0, 'DEC_DRIVER_TYPE': 1},
    {'RA_STEPPER_TYPE': 0, 'RA_DRIVER_TYPE': 2},
    {'DEC_STEPPER_TYPE': 0, 'DEC_DRIVER_TYPE': 2},
    {'RA_STEPPER_TYPE': 0, 'RA_DRIVER_TYPE': 3},
    {'DEC_STEPPER_TYPE': 0, 'DEC_DRIVER_TYPE': 3},
    {'RA_STEPPER_TYPE': 1, 'RA_DRIVER_TYPE': 0},
    {'DEC_STEPPER_TYPE': 1, 'DEC_DRIVER_TYPE': 0},
    {'PLATFORM': "0001", "BOARD": "1001"},
    {'PLATFORM': "1001", "BOARD": "0001"},
    {'PLATFORM': "1001", "BOARD": "0002"},
    {'PLATFORM': "1001", "BOARD": "0003"},
    {'PLATFORM': "1001", "BOARD": "0004"},
    {'BOARD': "1001", "USE_GPS": 1},
    {'BOARD': "1001", "USE_GYRO_LEVEL": 1},
    {'BOARD': "1001", "AZIMUTH_ALTITUDE_MOTORS": 1},
    {'BOARD': "1001", "DISPLAY_TYPE": 1},
    {'BOARD': "0002", "USE_GPS": 1},
    {'BOARD': "0002", "USE_GYRO_LEVEL": 1},
    {'BOARD': "0003", "USE_GPS": 1},
    {'BOARD': "0003", "USE_GYRO_LEVEL": 1},
    {'BOARD': "0004", "USE_GPS": 1},
    {'BOARD': "0004", "USE_GYRO_LEVEL": 1},
    {"AZIMUTH_ALTITUDE_MOTORS": 0, "AZ_STEPPER_TYPE": 1},
    {"AZIMUTH_ALTITUDE_MOTORS": 0, "AZ_DRIVER_TYPE": 1},
    {"AZIMUTH_ALTITUDE_MOTORS": 0, "AZ_DRIVER_TYPE": 2},
    {"AZIMUTH_ALTITUDE_MOTORS": 0, "AZ_DRIVER_TYPE": 3},
    {"AZ_STEPPER_TYPE": 1, "AZ_DRIVER_TYPE": 0},
    # actually possible combinations not to be handled by this script to reduce build times
    {'RA_STEPPER_TYPE': 0, 'DEC_STEPPER_TYPE': 1},
    {'RA_STEPPER_TYPE': 1, 'DEC_STEPPER_TYPE': 0},
]

# only allow same drivers for RA and DEC
for r in range(4):
    for d in range(4):
        if (r != d):
            filters.append(
                {'RA_DRIVER_TYPE': r, 'DEC_DRIVER_TYPE': d}
            )

# only allow same steppers for RA and DEC
for r in range(2):
    for d in range(2):
        if (r != d):
            filters.append(
                {'RA_STEPPER_TYPE': r, 'DEC_STEPPER_TYPE': d}
            )
            
# only allow same drivers for AZ and ALT
for r in range(4):
    for d in range(4):
        if (r != d):
            filters.append(
                {'AZ_DRIVER_TYPE': r, 'ALT_DRIVER_TYPE': d}
            )

# only allow same steppers for AZ and ALT
for r in range(2):
    for d in range(2):
        if (r != d):
            filters.append(
                {'AZ_STEPPER_TYPE': r, 'ALT_STEPPER_TYPE': d}
            )
            
# all boards and flags as value tuples, regardless of the filters
all_permutations = list(itertools.product(*(matrix.values())))

# all combinations as dict, regardless of the filters
all_combinations = []
for permutation in all_permutations:
    combination = {}
    combination_tuples = [(list(matrix.keys())[i], value)
                          for i, value in enumerate(permutation)]
    for t in combination_tuples:
        combination[t[0]] = t[1]
    all_combinations.append(combination)


def flagValueInCombination(flag, value, combination):
    return flag in combination and combination[flag] == value


def allowedCombination(combination):
    for f in filters:
        if all(item in combination.items() for item in f.items()):
            return False
    return True


allowed_combinations = list(filter(allowedCombination, all_combinations))
print(f"Testing {len(allowed_combinations)} permutations...")
time.sleep(3)

run_commands = []
for c in allowed_combinations:
    flags = ["-D {}={}".format(item[0], item[1]) for item in c.items()]
    flags_str = " ".join(flags)
    run_commands.append(
        {
            "env.PLATFORMIO_BUILD_FLAGS": flags_str,
            "command": "pio run -e {}".format(platforms[c['PLATFORM']])
        }
    )

# for i, command in enumerate(run_commands):
#     print("{}: {}".format(i, command))
# exit(0)

errors = []

for index,command in enumerate(run_commands):
    print(f"Building {index+1} of {len(allowed_combinations)} permutations...")
    print(command)
    os.environ['PLATFORMIO_BUILD_FLAGS'] = command['env.PLATFORMIO_BUILD_FLAGS']
    result = os.system(command['command'])
    if result:
        errors.append(command)
        if not CONTINUE_ON_ERROR:
            break

if errors:
    print("There were errors during the matrix build for following configurations:")
    for error in errors:
        print(error)
else:
    print(f"There were no errors found during the matrix build. {len(allowed_combinations)} permutations tested.")
