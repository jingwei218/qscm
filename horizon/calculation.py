from .models import *


def allocate_quantity(quantity_vector, criteria, quantity_matrix):
    """
    :param quantity_vector: 未分配数量的列表，每一项为(quantity, role, data_sheet_element category)
    :param criteria: 数量区间分配规则，每一项为[price category, price_conditions]
    :param quantity_matrix: 当前数据表的已分配的所有数量及其位置
    :param row: 当前行序号
    :return: quantity_matrix
    """

    number_of_criteria = len(criteria)

    # 自右向左遍历所有区间条件
    for i in range(number_of_criteria-1, -1, -1):
        price_category = criteria[i][0]  # 数量所对应分类，用于判断是否与数据行分类相同
        price_conditions = criteria[i][1]  # 价格条件，用于判断对应的数量是否位于区间内
        qty_range = dict()

        for price_condition in price_conditions:
            qty_range[price_condition.uom.name] = (price_condition.low, price_condition.high)

        row = 0
        for quantity in quantity_vector:
            qty = quantity[0]  # 数量对象
            qty_role = quantity[1]  # 数量类型
            qty_category = quantity[2]
            if price_category == qty_category:
                if qty_role == 'chgu':  # 直接判断所处位置
                    qty_uom = qty[0].uom.name
                    try:
                        if qty_range[qty_uom][0] <= qty[0].value <= qty_range[qty_uom][1]:  # 找到uom对应的最低/最高限额，判断是否在区间内
                            quantity_matrix[row][i] = qty[0].value
                    except KeyError:
                        pass
                elif qty_role == 'sapc':
                    qty_uom = qty[0].uom
                    if qty_uom == price_conditions[0].uom:  # 直接对应uom
                        quantity_matrix[row][i] = qty[0].value
                elif qty_role == 'md':
                    q_in_range = [False] * len(qty)  # 判断值列表，当判断值列表中所有的元素为True，则判定在区间内
                    i_q = 0  # 初始化q的序号
                    for q in qty:
                        q_uom = q.uom.name
                        try:
                            if qty_range[q_uom][0] <= q.value <= qty_range[q_uom][1]:  # 找到uom对应的最低/最高限额，判断当前量是否在区间内
                                q_in_range[i_q] = True
                                i_q += 1
                            else:
                                break
                        except KeyError:
                            continue
                    try:
                        q_in_range.index(False)
                    except ValueError:
                        quantity_matrix[row][i] = 1

            row += 1
    return quantity_matrix
