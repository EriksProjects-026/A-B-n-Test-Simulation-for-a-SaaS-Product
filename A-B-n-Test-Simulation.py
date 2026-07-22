import random
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

sns.set_theme(style="whitegrid")

#random.seed(1000) # я люблю когда с каждым запуском новые графики и можно увидеть как мог бы колебаться рынок и гипотезы могли бы меняться,
                                # но в целях эксперимента, чтобы не путать данные можете убрать хештег и все будет одинаково при каждом запуске)
GREEN = "\033[92m"
RED = "\033[91m"
RESET = "\033[0m"

GROUP_A = "A: Контрольная группа"
GROUP_B = "B: UX/СБП"
GROUP_C = "C: Агрессивный маркетинг"
GROUPS = [GROUP_A, GROUP_B, GROUP_C]


def calculate_loyal_users(cohorts, current_month): # здесь у нас будут собираться преданные пользователи, это очень важно для вдения статистики  у них другой коэфицент
    loyal_users = 0                                 # у них другой коэфицент того что они перестанут пользоваться программой, в течении трех месяцев их собираем потихоньку в когорту, а потом уже они становятся проверенными

    for cohort in cohorts:
        cohort_age = current_month - cohort["month"] + 1

        if cohort_age >= 3:
            loyal_users += cohort["active_users"]

    return int(loyal_users)


def get_profit(active_users, group, month):
    if group == GROUP_A:
        profit_rate = 96
    elif group == GROUP_B:
        profit_rate = 125
    else:
        # У C прибыль с пользователя ниже из-за скидок и бесплатных пробных периодов.
        profit_rate = 100

    if group == GROUP_B:
        monthly_change = random.uniform(0.87, 1.19)
    elif group == GROUP_C:
        monthly_change = random.uniform(0.77, 1.32)
    else:
        monthly_change = random.uniform(0.83, 1.14)

    # В конце года эфект скидочной кампании C становится еще слабее, те кто хотели купить подписку на год, уже купили и не нуждаются в ней,
    if group == GROUP_C and month >= 7: # из-за этого еще больше новых юзеров из общей массыбудет использовать платформу на "халяву", и отменять подписку через месяц.
        monthly_change *= 0.94

    profit = active_users * profit_rate * monthly_change
    return round(profit)


def generate_data():
    rows = []
    previous_active_users = {}
    cohorts_by_group = {}
# создали будущую загатовку под датафрейм, и сетчик когорт в группе, и предыдущих активных пользователей
    for group in GROUPS:
        previous_active_users[group] = 0
        cohorts_by_group[group] = []

    for month in range(1, 13):
        for group in GROUPS:
            if group == GROUP_A:
                base_values = [430, 470, 505, 555, 590, 625, 650, 690, 720, 790, 835, 880]
                random_change = random.randint(-65, 75)
            elif group == GROUP_B:
                base_values = [680, 720, 770, 860, 960, 1060, 1170, 1300, 1450, 1640, 1840, 2070]
                random_change = random.randint(-180, 250)
            else:
                base_values = [3500, 650, 720, 1300, 1700, 1900, 1300, 1000, 800, 900, 1000, 1100]
                if month >= 7:
                    random_change = random.randint(-800, 900)
                else:
                    random_change = random.randint(-220, 320)    # такие строгие значения в списказ а не полный рандом, потому что я симулирую рынок с определным поведением

            new_users = base_values[month - 1] + random_change

            previous_users = previous_active_users[group]   #предыдущие активные пользователи, т.к. первый месяц они равны нулю пока что

            if group == GROUP_A:
                base_churn_rates = [0.02, 0.025, 0.022, 0.024, 0.026, 0.025,
                                    0.028, 0.027, 0.03, 0.032, 0.031, 0.03]
                churn_change = random.uniform(-0.02, 0.02)
            elif group == GROUP_B:
                base_churn_rates = [0.018, 0.02, 0.019, 0.021, 0.02, 0.022,
                                    0.021, 0.023, 0.022, 0.024, 0.023, 0.022]
                churn_change = random.uniform(-0.02, 0.02)
            else:
                # Во 2-3 месяце заканчивается бесплатный период.
                base_churn_rates = [0.01, 0.55, 0.48, 0.08, 0.07, 0.06,
                                    0.055, 0.05, 0.05, 0.048, 0.045, 0.045]
                churn_change = random.uniform(-0.08, 0.08)

            churn_rate = base_churn_rates[month - 1] + churn_change
            churn_rate = max(churn_rate, 0)

            churn_users = int(previous_users * churn_rate)   # сколько челов ушло

            active_users = previous_users + new_users - churn_users
            active_users = max(active_users, 0)       # сколько стало активных юзеров + проверка чтобы не было ниже 0, минусовое количество юзеров это бред

            # Постоянные и лояльные пользователи обычно уходят заметно реже. 3 месяца подиски = постоянник
            for cohort in cohorts_by_group[group]:
                cohort_age = month - cohort["month"] + 1
                if cohort_age >= 3:
                    cohort_churn_rate = churn_rate * random.uniform(0.2, 0.3)
                else:
                    cohort_churn_rate = churn_rate

                cohort_users_after_churn = cohort["active_users"] * (1 - cohort_churn_rate)
                cohort["active_users"] = int(cohort_users_after_churn)       #посчитали сколько в когорте юзеров мечущих стать лояльными осталось в другом месяце

            new_cohort = {
                "month": month,
                "active_users": new_users,
            }
            cohorts_by_group[group].append(new_cohort) # создаем когорту юзеров и добавляем этот словарь в список когорт определенной группы

            loyal_users = calculate_loyal_users(
                cohorts_by_group[group],
                month,
            )
            loyal_users = min(loyal_users, active_users)   # считаем сколько пользователей из когорт уже стали постоянными клиентами, при этом они не могу превышать активных юзеров, иначе билеберда какая то

            profit = get_profit(active_users, group, month) # cчитаем чистую прибыль ( этот скрипт создан как проект для того чтобы показать как работают A/B/n тесты, поэтому над этим я не замарочился)

            rows.append(
                {
                    "Month": month,
                    "Group": group,
                    "New Users": new_users,
                    "Churn Users": churn_users,
                    "Active Users": active_users,
                    "Loyal Users": loyal_users,
                    "Profit": profit,
                }
            )                  # Добавляем словарь в список словарей из которых потом будет образован датафрейм

            previous_active_users[group] = active_users  # старые юзеры у этой группы в некст месяце - это активные юзеры в этом месяце

    return pd.DataFrame(rows)


def make_charts(data):
    colors = {
        GROUP_A: "#4C78A8",
        GROUP_B: "#F58518",
        GROUP_C: "#E45756",
    }   # задаем цвета группам на графике

    figure, axes = plt.subplots(1, 2, figsize=(16, 6))

    sns.lineplot(
        data=data,
        x="Month",
        y="Active Users",
        hue="Group",
        hue_order=GROUPS,
        palette=colors,
        marker="o",
        linewidth=2.5,
        ax=axes[0],
    )
    axes[0].set_title("Динамика активных пользователей")
    axes[0].set_xlabel("Месяцы")
    axes[0].set_ylabel("Количество пользователей")
    axes[0].set_xticks(range(1, 13))
    axes[0].set_xticklabels([f"{month:02d}" for month in range(1, 13)])
    axes[0].legend(title="Группа")       # создание графика для сравнения роста юзеров в течение года для всех групп

    sns.lineplot(
        data=data,
        x="Month",
        y="Profit",
        hue="Group",
        hue_order=GROUPS,
        palette=colors,
        marker="o",
        linewidth=2.5,
        ax=axes[1],
    )
    axes[1].set_title("Динамика чистой прибыли")
    axes[1].set_xlabel("Месяцы")
    axes[1].set_ylabel("Чистая прибыль")
    axes[1].set_xticks(range(1, 13))
    axes[1].set_xticklabels([f"{month:02d}" for month in range(1, 13)])
    axes[1].ticklabel_format(axis="y", style="plain", useOffset=False)
    axes[1].legend(title="Группа")              # создание графика для сравнения роста чистой прибыли в течение года для всех групп

    figure.suptitle("Результаты A/B/C-теста SaaS-продукта", fontsize=15)
    figure.tight_layout()
    plt.show()


def print_hypothesis(index, description, condition):
    color = GREEN if condition else RED
    answer = "Да" if condition else "Нет"
    print(f"{color}{index}. {description}: {answer}{RESET}") #красивый вывод гипотиз разным цветом, моя любимая фишка, добавляет живую и яркую атмосферу в серый терминал


def print_analytics(data):
    print("\nСВОДКА ПО ГРУППАМ")
    print("-" * 70)

    for group in GROUPS:
        group_data = data[data["Group"] == group]
        last_month = group_data[group_data["Month"] == 12].iloc[0]
        average_profit = group_data["Profit"].mean()

        print(f"{group}")
        print(f"Средняя чистая прибыль: {average_profit:,.0f}₽")
        print(f"Постоянные пользователи в 12 месяце: {int(last_month['Loyal Users'])}")
        print(f"Активные пользователи в 12 месяце: {int(last_month['Active Users'])}")
        print(f"Чистая прибыль в 12 месяце: {last_month['Profit']:,.0f}₽\n")  # функция - красивый вывод итого статистики за год по каждой группе

    first_quarter = data[data["Month"].isin([1, 2, 3])]
    c_churn = first_quarter[first_quarter["Group"] == GROUP_C]["Churn Users"].sum()
    a_b_churn = first_quarter[first_quarter["Group"].isin([GROUP_A, GROUP_B])]["Churn Users"].sum()
    condition_1 = c_churn > a_b_churn
    print_hypothesis(
        1,
        "Количество отписок группы C в первом квартале больше, чем у групп A и B вместе", # проверяем гипотизы и выводим их
        condition_1,
    )
     #Profit B в 6 месяце > Profit C в 6 месяце, проверяем и выводим эту гипотезу
    profit_b_in_6month = data[(data["Group"] == GROUP_B) & (data["Month"] == 6)]["Profit"].iloc[0]
    profit_c_in_6month = data[(data["Group"] == GROUP_C) & (data["Month"] == 6)]["Profit"].iloc[0]
    condition_2 = profit_b_in_6month > profit_c_in_6month
    print_hypothesis(
        2,
        "Чистая прибыль за июнь у группы B больше, чем у группы C",
        condition_2,
    )

    first_half = data[(data["Group"] == GROUP_C) & (data["Month"] <= 6)]
    second_half = data[(data["Group"] == GROUP_C) & (data["Month"] >= 7)]
    condition_3 = second_half["New Users"].sum() < first_half["New Users"].sum()
    print_hypothesis(
        3,
        "Количество новых пользователей группы C во втором полугодии меньше, чем в первом",
        condition_3,
    )

    # в августе количество активных пользователей у B больше чем у С.
    B_users_in8month = data[(data["Group"] == GROUP_B) & (data["Month"] == 8)]["Active Users"].iloc[0]
    C_users_in8month = data[(data["Group"] == GROUP_C) & (data["Month"] == 8)]["Active Users"].iloc[0]
    condition_4 = B_users_in8month > C_users_in8month
    print_hypothesis(
        4,
        " Активных пользователей в августе у группы B больше, чем у группы С",
        condition_4,
    )

    last_month_data = data[data["Month"] == 12]
    b_loyal = last_month_data[last_month_data["Group"] == GROUP_B]["Loyal Users"].iloc[0]
    condition_5 = b_loyal == last_month_data["Loyal Users"].max()
    print_hypothesis(
        5,
        "Количество постоянных пользователей группы B в 12 месяце максимальное",
        condition_5,
    )

    winner_row = last_month_data.sort_values("Loyal Users", ascending=False).iloc[0] # выбираем победителя по количеству лояльных и постоянных клиентов на последний месяц
    print(f"\n{GREEN}ПОБЕДИТЕЛЬ: {winner_row['Group']}{RESET}")                # так как это фундамент будущего сервиса, его клиенты, зачем делать продукт если у него
                                                                          # нет нет клиентов? берем постоянников, ведь мы для всех пытаемся создать лучший сервис,
def main():                                                          # но у кого больше постоянников значит та стратегия и удерэала больше новых клиентов
    data = generate_data()

    print("Первые строки сгенерированного DataFrame:")
    print(data.head(9).to_string(index=False)) # выводим первы строки датафрейма без индексов

    print_analytics(data)  #выводим сводку по итогам статистики каждой из групп и проверку гипотез
    make_charts(data)   # выводим и показываем график
main()
