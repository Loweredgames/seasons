import copy
import json
import os
import os.path as path
import imageio.v3 as imageio
import numpy.typing
from colorsys import rgb_to_hsv, hsv_to_rgb

template_folder = 'templates'
output_folder = 'data/seasons/functions/generated'

vanilla_biome_folder = 'vanilla/biome'
vanilla_grass_texture = 'vanilla/grass.png'
vanilla_foliage_texture = 'vanilla/foliage.png'

tag_file = 'data/seasons/tags/blocks/snowable_plants.json'
biome_tag_folder = 'data/seasons/tags/worldgen/biome'
biome_folder = 'data/seasons/worldgen/biome'

seasons = ['summer', 'fall', 'winter', 'spring']

# Constants

snowy_ground = 'F4FEFF'

flowering_leaves = 'FF8CAF'
winter_branches = '7C6952'
snowy_leaves = 'FFFFFF'

fall_grass = [-35, -25, -5]
winter_grass = [-38, -55, -5]
spring_grass = [1, -10, 0]

# TODO: apply these!
fall_sky = [0, -20, -10]
winter_sky = [0, -28, -15]
spring_sky = [0, 0, 0]

early_fall_leaves = [-59, -10, 32]
late_fall_leaves = [-97, 11, -16]
spring_leaves = [0, 5, 32]

fall_temperature = -0.4
winter_temperature = -0.8
spring_temperature = -0.3

# Conversions
to_summer_grass = {
    'default': {
        'fall': [-x for x in fall_grass],
        'winter': [-x for x in winter_grass],
        'spring': [-x for x in spring_grass]
    },
    'summer_rains': {
        'fall': [0, 0, 0],
        'winter': [0, 0, 0],
        'spring': [0, 0, 0]
    }
}

to_summer_foliage = {
    'default': {
        'fall': [-x for x in early_fall_leaves],
        'winter': [0, 0, 0], # Assuming vanilla winter biome tint as summer
        'spring': [-x for x in spring_leaves]
    },
    'summer_rains': {
        'fall': [0, 0, 0],
        'winter': [0, 0, 0],
        'spring': [0, 0, 0]
    }
}

to_summer_temperature = {
    'default': {
        'fall': -fall_temperature,
        'winter': -winter_temperature,
        'spring': -spring_temperature
    },
    'summer_rains': {
        'fall': 0,
        'winter': 0,
        'spring': 0
    }
}

# Permanently summer: warm_ocean, badlands, desert, eroded_badlands, jungle, sparse jungle, mangrove swamp, wooded_badlands
# Permanently winter: frozen_peaks, ice_spikes, frozen_ocean, deep_frozen_ocean
# ???: Lukewarm ocean, swamp

# Mapping of biomes from vanilla biomes per season
# default: leaves shift colors, snowy winters, melting spring
# summer_rains: rain period in summer, dry all other seasons

season_biomes = {
    'beach': {
        'v_summer': 'beach',
        'v_winter': 'snowy_beach'
    },
    'birch_forest': {
        'v_summer': 'birch_forest'
    },
    'ocean': {
        'v_winter': 'cold_ocean',
        'v_summer': 'ocean',
        'winter': {
            'temperature': -0.3
        }
    },
    'dark_forest': {
        'v_summer': 'dark_forest'
    },
    'deep_ocean': {
        'v_winter': 'deep_cold_ocean',
        'v_summer': 'deep_ocean',
        'winter': {
            'temperature': -0.3
        }
    },
    'flower_forest': {
        'v_summer': 'flower_forest'
    },
    'forest': {
        'v_summer': 'forest'
    },
    'peaks': {
        'v_summer': 'stony_peaks',
        'v_winter': 'jagged_peaks'
    },
    'river': {
        'v_summer': 'river',
        'v_winter': 'frozen_river'
    },
    'grove': {
        'v_winter': 'grove'
    },
    'meadow': {
        'v_summer': 'meadow'
    },
    'mushroom_fields': {
        'v_summer': 'mushroom_fields'
    },
    'old_growth_birch_forest': {
        'v_summer': 'old_growth_birch_forest'
    },
    'old_growth_pine_taiga': {
        'v_fall': 'old_growth_pine_taiga'
    },
    'old_growth_spruce_taiga': {
        'v_fall': 'old_growth_spruce_taiga'
    },
    'plains': {
        'v_summer': ['plains', 'sunflower_plains'],
        'v_winter': 'snowy_plains'
    },
    'savanna': {
        'v_winter': ['savanna', 'windswept_savanna'],
        'type': 'summer_rains'
    },
    'savanna_plateau': {
        'v_winter': ['savanna_plateau'],
        'type': 'summer_rains'
    },
    'taiga': {
        'v_summer': 'taiga',
        'v_winter': 'snowy_taiga',
        'default': {
            'temperature': 0.5
        }
    },
    'stony_shore': {
        'v_fall': 'stony_shore'
    },
    'windswept_hills': {
        'v_spring': ['windswept_forest', 'windswept_gravelly_hills', 'windswept_hills']
    }
}

with open(tag_file) as file:
    data = json.load(file)
    values = data['values']

def instantiate_template(type, values):
    folder = template_folder + '/' + type
    for filename in os.listdir(folder):
        template_path = path.join(folder, filename)
        if not path.isfile(template_path):
            continue

        with open(template_path) as file:
            template = file.read()
    
        with open(path.join(output_folder, filename), 'w') as file:
            for value in values:
                file.write(template.replace(f'${type}', value))

instantiate_template('plant', values)

vanilla_grass_image = imageio.imread(vanilla_grass_texture)
vanilla_foliage_image = imageio.imread(vanilla_foliage_texture)

def union(*args) -> list:
    result = []
    for l in args:
        result.extend(l)
    return result

def add_if_present(biomes: list, biome: dict, key: str):
    if key not in biome:
        return

    entry = biome[key]
    if isinstance(entry, list):
        biomes.extend([f'minecraft:{x}' for x in entry])
    else:
        biomes.append(f'minecraft:{entry}')

def hex_to_rgb(s: str) -> list:
    r = s[0:2]
    g = s[2:4]
    b = s[4:6]
    return tuple([int(x, 16) for x in [r, g, b]])

def write_tag(id: str, biomes: list):
    data = {
        'replace': False,
        'values': biomes
    }
    with open(f'{biome_tag_folder}/{id}.json', 'w') as file:
        json.dump(data, file, indent=4)

def create_tags(id, biome, winter_biomes: list, bare_winter_biomes: list):
    summer_list = [f'seasons:summer/{id}']
    fall_list = [f'seasons:fall_early/{id}', f'seasons:fall_late/{id}']
    bare_winter_biome = f'seasons:winter_bare/{id}'
    winter_list = [bare_winter_biome, f'seasons:winter_snowy/{id}']
    spring_list = [f'seasons:winter_melting/{id}', f'seasons:spring_default/{id}', f'seasons:spring_flowering/{id}']

    winter_biomes.extend(winter_list)
    bare_winter_biomes.append(bare_winter_biome)

    vanilla = []
    for season in seasons:
        add_if_present(vanilla, biome, f'v_{season}')

    non_summer = union(vanilla, fall_list, winter_list, spring_list)
    non_fall = union(vanilla, summer_list, winter_list, spring_list)
    non_winter = union(vanilla, summer_list, fall_list, spring_list)
    non_spring = union(vanilla, summer_list, fall_list, winter_list)

    write_tag(f'non_summer/{id}', non_summer)
    write_tag(f'non_fall/{id}', non_fall)
    write_tag(f'non_winter/{id}', non_winter)
    write_tag(f'non_spring/{id}', non_spring)

def int_to_rgb(color: int) -> tuple:
    r = (color >> 16) & 0xff
    g = (color >> 8) & 0xff
    b = color & 0xff
    return r, g, b

def rgb_to_int(r: int, g: int, b: int) -> int:
    return ((int(r) & 0xff) << 16) | ((int(g) & 0xff) << 8) | (int(b) & 0xff)

def calculate_color(downfall: float, temperature: float, colormap: numpy.typing.NDArray) -> int:
    product = downfall * temperature
    x = int((1.0 - temperature) * 255.0)
    y = int((1.0 - product) * 255.0)
    if y >= colormap.shape[0] or x >= colormap.shape[1]:
        return -65281

    pixel = colormap[y, x]
    return rgb_to_int(pixel[0], pixel[1], pixel[2])

def remap_color(color: int, mapping: list) -> int:
    r, g, b = int_to_rgb(color)
    h, s, v = rgb_to_hsv(r, g, b)
    h += mapping[0]
    s += mapping[1]
    v += mapping[2]
    r, g, b = hsv_to_rgb(h, s, v)
    return rgb_to_int(r, g, b)

def load_biome(id: str):
    filename = f'{vanilla_biome_folder}/{id}.json'
    with open(filename, 'r') as file:
        biome = json.load(file)
    set_default_colors(biome)
    return biome

def set_default_colors(biome):
    effects = biome['effects']
    downfall = biome['downfall']
    temperature = biome['temperature']
    if 'grass_color' not in effects:
        effects['grass_color'] = calculate_color(downfall, temperature, vanilla_grass_image)
    if 'foliage_color' not in effects:
        effects['foliage_color'] = calculate_color(downfall, temperature, vanilla_foliage_image)

def get_first_template(biome, season):
    key = f'v_{season}'
    template = biome.get(key, None)
    if isinstance(template, list):
        return template[0]
    return template

def remap(biome, key, mapping):
    effects = biome['effects']
    effects[key] = remap_color(effects[key], mapping)

def set_color(biome, key, hex):
    r, g, b = hex_to_rgb(hex)
    effects = biome['effects']
    effects[key] = rgb_to_int(r, g, b)

def apply_overrides(biome_data, conversion, season):
    if not season in conversion:
        return
    for key, item in conversion[season].items():
        biome_data[key] = item

def update_precipitation(biome):
    if biome['precipitation'] == 'none':
        return
    temperature = biome['temperature']
    if temperature < 0.15:
        biome['precipitation'] = 'snow'
    else:
        biome['precipitation'] = 'rain'

def write_biome(id, biome, season):
    with open(f'{biome_folder}/{season}/{id}.json', 'w') as file:
        json.dump(biome, file, indent=2)

def create_biomes(id: str, biome: dict):
    type = biome.get('type', 'default')
    templates = {}
    for season in seasons:
        templates[season] = get_first_template(biome, season)
    
    if templates['summer'] is not None:
        template = load_biome(templates['summer'])
    else:
        # Try to find a fallback and use as template
        for season in seasons:
            other_template = templates[season]
            if other_template is not None:
                template = load_biome(other_template)
                template['temperature'] += to_summer_temperature[type][season]
                set_default_colors(template)
                break

    apply_overrides(template, biome, 'default')

    if type == 'default':
        summer = copy.deepcopy(template)
        update_precipitation(summer)
        write_biome(id, summer, 'summer')

        if templates['fall']:
            fall_template = load_biome(templates['fall'])
        else:
            fall_template = None
        
        if fall_template:
            fall_early = copy.deepcopy(fall_template)
        else:
            fall_early = copy.deepcopy(template)
            fall_early['temperature'] += fall_temperature
            remap(fall_early, 'grass_color', fall_grass)
        # Vanilla doesn't have fall colors, so just transform as if the template was summer regardless
        remap(fall_early, 'foliage_color', early_fall_leaves)
        apply_overrides(fall_early, biome, 'fall')
        update_precipitation(fall_early)
        write_biome(id, fall_early, 'fall_early')

        if fall_template:
            fall_late = copy.deepcopy(fall_template)
        else:
            fall_late = copy.deepcopy(template)
            fall_late['temperature'] += fall_temperature
            remap(fall_late, 'grass_color', fall_grass)
        # Vanilla doesn't have fall colors, so just transform as if the template was summer regardless
        remap(fall_late, 'foliage_color', late_fall_leaves)
        apply_overrides(fall_late, biome, 'fall')
        update_precipitation(fall_late)
        write_biome(id, fall_late, 'fall_late')

        if templates['winter']:
            winter_template = load_biome(templates['winter'])
        else:
            winter_template = None

        if winter_template:
            winter_bare = copy.deepcopy(winter_template)
        else:
            winter_bare = copy.deepcopy(template)
            winter_bare['temperature'] += winter_temperature
            remap(winter_bare, 'grass_color', winter_grass)
        set_color(winter_bare, 'foliage_color', winter_branches)
        apply_overrides(winter_bare, biome, 'winter')
        update_precipitation(winter_bare)
        if winter_bare['precipitation'] != 'snow':
            print(f'Warning: winter biome for {id} doesnt snow')
        write_biome(id, winter_bare, 'winter_bare')

        winter_snowy = copy.deepcopy(winter_bare)
        set_color(winter_snowy, 'grass_color', snowy_ground)
        set_color(winter_snowy, 'foliage_color', snowy_leaves)
        write_biome(id, winter_snowy, 'winter_snowy')

        winter_melting = copy.deepcopy(winter_snowy)
        winter_melting['temperature'] = template['temperature'] + spring_temperature
        if 'spring' in biome and 'temperature' in biome['spring']:
            winter_melting['temperature'] = biome['spring']['temperature']
        update_precipitation(winter_melting)
        if winter_melting['precipitation'] != 'rain':
            print(f'Warning: melting winter biome for {id} snows')
        write_biome(id, winter_melting, 'winter_melting')

        if templates['spring']:
            spring_template = load_biome(templates['spring'])
        else:
            spring_template = None

        if spring_template:
            spring_default = copy.deepcopy(spring_template)
        else:
            spring_default = copy.deepcopy(template)
            spring_default['temperature'] += spring_temperature
        remap(spring_default, 'grass_color', spring_grass)
        remap(spring_default, 'foliage_color', spring_leaves)
        apply_overrides(spring_default, biome, 'spring')
        update_precipitation(spring_default)
        write_biome(id, spring_default, 'spring_default')

        spring_flowering = copy.deepcopy(spring_default)
        set_color(spring_flowering, 'foliage_color', flowering_leaves)
        write_biome(id, spring_flowering, 'spring_flowering')

    elif type == 'summer_rains':
        # TODO
        pass

    else:
        raise Exception('Unknown type')

winter_biomes = []
bare_winter_biomes = []
for id, biome in season_biomes.items():
    create_tags(id, biome, winter_biomes, bare_winter_biomes)
    create_biomes(id, biome)

write_tag(f'winter', winter_biomes)
write_tag(f'bare_winter', bare_winter_biomes)

instantiate_template('biome', season_biomes.keys())
