import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt

# Это тестовый скрипт для генерации и визуализации гистограмм
# распределения возрастов смертей и возрастов размножения существ
# в популяции, с целью анализа отбора по возрасту размножения.
# также тут видно какот тип данных удобен для хранения информации 
# о смертях и датах рождения и поколениях.

creatures_amount = 10000
max_age = 500
mu = 370 # average lifespan
sigma = mu / 10 # standard deviation
reprod_ages = [350, 400, 450]
reprod_deviation = 10
bins_count = 50


# Опишем структуру данных для ханения исторической информации о поколениях, смертях, 
# а также о возрастах размножения каждого существа
# эти данные позволят опредялять качественные характеристики отбора
INT32 = np.int32
FLOAT32 = np.float32
dtype_population_data = np.dtype([
    ('id', INT32),
    ('generation', INT32),
    ('age', INT32),
    ('reprod_ages', INT32, (3,))
])


def normal_distribution(x, mu=0, sigma=1):
    coef = 1 / (sigma * np.sqrt(2 * np.pi))
    exponent = -0.5 * ((x - mu) / sigma) ** 2
    return coef * np.exp(exponent)


def random_variation(base_ages: list, deviation: int) -> list:
    varied_ages = []
    for age in base_ages:
        variation = np.random.normal(0, deviation)
        varied_ages.append(age + variation)
    return varied_ages


def generate_population_data():
    # выделим память, пока заполним все нулями
    result = np.zeros(creatures_amount, dtype=dtype_population_data)

    # сгенерируем данные по id и поколению
    result['id'] = np.arange(creatures_amount, dtype=INT32)
    result['generation'] = np.zeros(creatures_amount, dtype=INT32)

    # сгенерируем данные по смертям
    creatures_deaths = np.random.normal(mu, sigma, creatures_amount)
    for cd in creatures_deaths:
        if cd < 0:
            creatures_deaths[creatures_deaths == cd] = 0
        elif cd > max_age:
            creatures_deaths[creatures_deaths == cd] = max_age
    result['age'] = creatures_deaths.astype(INT32)

    # генерация возрастов размножения с вариациями
    creatures_reprod_ages = []
    for cr in range(creatures_amount):
        creature_reprod_ages = random_variation(reprod_ages, reprod_deviation)
        creatures_reprod_ages.append(creature_reprod_ages)
    result['reprod_ages'] = np.array(creatures_reprod_ages, dtype=INT32)

    # напечатать срез данных для проверки
    # print("Sample population data (first 5 creatures):")
    # print(result[:5])
    # пример вывода:
    #     [
    #         (0, 0, 344, [348, 410, 446])
    #         (1, 0, 347, [369, 396, 453])
    #         (2, 0, 416, [353, 422, 453])
    #         (3, 0, 390, [341, 392, 427])
    #         (4, 0, 364, [333, 415, 430])
    #     ]
    
    return result


def filter_post_mortum_reprod_ages(data):
    # cut off reproduction ages older then death age
    for i in range(len(data)):
        death_age = data['age'][i]
        reprod_ages_list = data['reprod_ages'][i].tolist()
        filtered_reprod_ages = [age for age in reprod_ages_list if age < death_age]
        # pad with -1 to keep the shape
        while len(filtered_reprod_ages) < 3:
            filtered_reprod_ages.append(-1)
        data['reprod_ages'][i] = np.array(filtered_reprod_ages, dtype=INT32)
    return data


def plot_population(data, reprod_ages):
    """
    Filter reproduction ages and plot histograms of death ages and reproduction ages.
    
    Args:
        data: Population data array
        reprod_ages: List of base reproduction ages
    """
    

    # PLOTTING START
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 10))

    # First subplot: Death ages distribution
    ax1.hist(data['age'], bins=bins_count, density=True, alpha=0.6, color='g', label='Death ages')
    # add base reproduction age markers to first subplot
    for age in reprod_ages:
        ax1.axvline(x=age, color='r', linestyle='--', linewidth=2)

    ax1.legend()
    ax1.set_xlabel('Age')
    ax1.set_ylabel('Density')
    ax1.set_title('Death Ages Distribution')
    ax1.grid(True)

    # Second subplot: Reproduction ages distribution
    # Flatten all reproduction ages
    all_reprod_ages = []
    for creature_ages in data['reprod_ages']:
        all_reprod_ages.extend([age for age in creature_ages if age != -1])

    # Plot reproduction ages distribution
    ax2.hist(all_reprod_ages, bins=bins_count, density=True, alpha=0.6, color='b', label='Reproduction ages')

    # add base reproduction age markers to second subplot
    for age in reprod_ages:
        ax2.axvline(x=age, color='r', linestyle='--', linewidth=2)

    ax2.legend()
    ax2.set_xlabel('Age')
    ax2.set_ylabel('Density')
    ax2.set_title('Reproduction Ages Distribution')
    ax2.grid(True)

    # Set equal x-axis scales for both subplots
    max_age_value = max(max(data['age']), max(all_reprod_ages) if all_reprod_ages else 0)
    ax1.set_xlim(0, max_age_value)
    ax2.set_xlim(0, max_age_value)

    plt.tight_layout()
    plt.show()



# Generate population data
data=generate_population_data()

# Тут можно отлильтровать данные для гистограммы, сделать нужный срез данных
# сделаем срез только 100 последний существ, а не по всем данным
# data - это все данные по популяции накопленные в процессе моделирования
# data = data[-500:] # это срез последних 500 существ
# здесь также можно сделать срез по поколениям, если бы у нас было несколько поколений в данных

# отфильтруем возраста размножения, которые наступают после смерти
data = filter_post_mortum_reprod_ages(data)

# рисуем графики
plot_population(data, reprod_ages)
