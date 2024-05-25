# Импортируем необходимые библиотеки и модули
from ursina.prefabs.first_person_controller import FirstPersonController
from ursina import *
from ursina.shaders import basic_lighting_shader
from numpy import floor
from perlin_noise import PerlinNoise
import json
import os

# Настройка параметров шума и генерации ландшафта
noise = PerlinNoise(octaves=2, seed=1488)
amp = 6
freq = 24
terrain_width = 25

# Инициализация ландшафта
landscape = [[0 for _ in range(terrain_width)] for _ in range(terrain_width)]

for position in range(terrain_width**2):
    x = floor(position / terrain_width)
    z = floor(position % terrain_width)
    y = floor(noise([x / freq, z / freq]) * amp)
    landscape[int(x)][int(z)] = int(y)

# Инициализация приложения Ursina
app = Ursina()

# Настройка текстуры неба
sky_texture = load_texture('assets/skybox.jpg')
sky = Entity(
    model='sphere',
    texture=sky_texture,
    scale=1000,
    double_sided=True
)

# Загрузка текстур
grass_texture = load_texture('assets/grass.jpg')
lava_texture = load_texture('assets/lava.png')
leaves_texture = load_texture('assets/leaves.png')
wood_texture = load_texture('assets/wood.png')
water_texture = load_texture('assets/water.png')

# Словарь текстур
textures = {
    '1': grass_texture,
    '2': lava_texture,
    '3': leaves_texture,
    '4': wood_texture,
    '5': water_texture
}

# Переменная для отслеживания текущей текстуры
current_texture = grass_texture

# Функция для переключения текстур
def switch_texture(key):
    global current_texture
    if key in textures:
        current_texture = textures[key]

# Создаем класс Voxel на основе Button
class Voxel(Button):
    def __init__(self, position=(0, 0, 0), texture=grass_texture):
        super().__init__(
            parent=scene,
            model='cube',
            texture=texture,
            position=position,
            origin_y=0.5,
            color=color.color(0, 0, random.uniform(0.9, 1)),
            shader=basic_lighting_shader
        )

    # Обработка взаимодействия с блоками Voxel
    def input(self, key):
        if self.hovered:
            if key == 'right mouse down':
                voxel = Voxel(position=self.position + mouse.normal, texture=current_texture)
                voxels.append(voxel)
            if key == 'left mouse down':
                if self in voxels:
                    voxels.remove(self)
                destroy(self)

# Генерация платформы из блоков Voxel
voxels = []
for x_dynamic in range(terrain_width):
    for z_dynamic in range(terrain_width):
        voxel = Voxel(position=(x_dynamic, landscape[x_dynamic][z_dynamic], z_dynamic))
        voxels.append(voxel)

# Добавляем персонажа
player = FirstPersonController()

# Изменяем FOV (поле зрения) камеры
camera.fov = 120

# Начальная позиция для телепортации игрока при падении
initial_position = Vec3(terrain_width // 2, 10, terrain_width // 2)

# Устанавливаем начальную позицию игрока
player.position = initial_position

# Функция для проверки высоты игрока и телепортации на поверхность
def check_player_height():
    if player.y < -10:  # Если игрок ниже этой высоты, телепортируем его
        player.position = initial_position

# Функция обновления, которая вызывается каждый кадр
def update():
    check_player_height()

# Функция ввода для переключения текстур
def input(key):
    switch_texture(key)
    if key == 'f5':
        save_world()
    elif key == 'f9':
        load_world()

# Функция сохранения мира
def save_world():
    world_data = [{'position': (voxel.position.x, voxel.position.y, voxel.position.z), 'texture': texture_to_key(voxel.texture)} for voxel in voxels]
    with open('level.dat', 'w') as f:
        json.dump(world_data, f)
    print('World saved.')

# Преобразование текстуры в ключ для сохранения
def texture_to_key(texture):
    for key, value in textures.items():
        if value == texture:
            return key
    return '1'  # Значение по умолчанию

# Функция загрузки мира
def load_world():
    global voxels
    if os.path.exists('level.dat'):
        with open('level.dat', 'r') as f:
            world_data = json.load(f)
        # Удаляем все текущие воксели
        for voxel in voxels:
            destroy(voxel)
        voxels = []
        for data in world_data:
            position = Vec3(*data['position'])
            texture = textures[data['texture']]
            voxel = Voxel(position=position, texture=texture)
            voxels.append(voxel)
        print('World loaded.')

# Запуск приложения
app.run()
