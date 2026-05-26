import math


def calculate_bmi(weight_kg, height_cm):
    if weight_kg <= 0:
        raise ValueError("peso deve ser maior que zero")

    height_m = height_cm / 100
    if height_m <= 0:
        raise ValueError("altura deve ser maior que zero")
    return round(weight_kg / (height_m**2), 2)


def calculate_waist_height_ratio(waist_cm, height_cm):
    if waist_cm <= 0:
        raise ValueError("cintura deve ser maior que zero")
    if height_cm <= 0:
        raise ValueError("altura deve ser maior que zero")
    return round(waist_cm / height_cm, 3)


def calculate_us_navy_bodyfat(sex, height_cm, neck_cm, waist_cm, hip_cm=None):
    normalized_sex = str(sex).lower()
    if height_cm <= 0 or neck_cm <= 0 or waist_cm <= 0:
        raise ValueError("altura, pescoco e cintura devem ser maiores que zero")

    if normalized_sex in {"male", "m", "masculino"}:
        if waist_cm <= neck_cm:
            raise ValueError("cintura deve ser maior que pescoco para o metodo da Marinha")
        height_in = height_cm / 2.54
        neck_in = neck_cm / 2.54
        waist_in = waist_cm / 2.54
        result = (
            86.010 * math.log10(waist_in - neck_in)
            - 70.041 * math.log10(height_in)
            + 36.76
        )
    elif normalized_sex in {"female", "f", "feminino"}:
        if hip_cm is None or hip_cm <= 0:
            raise ValueError("quadril e obrigatorio para mulheres no metodo da Marinha")
        if waist_cm + hip_cm <= neck_cm:
            raise ValueError("cintura + quadril deve ser maior que pescoco")
        height_in = height_cm / 2.54
        neck_in = neck_cm / 2.54
        waist_in = waist_cm / 2.54
        hip_in = hip_cm / 2.54
        result = (
            163.205 * math.log10(waist_in + hip_in - neck_in)
            - 97.684 * math.log10(height_in)
            - 78.387
        )
    else:
        raise ValueError("sexo deve ser 'male' ou 'female'")

    return round(result, 2)
