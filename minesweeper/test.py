import logging
import minesweeper as ms
from bfs import BreathFirstSearch
from csp import CSP_agent
from RL import Reinforcement

statistics = {'size': '8 * 8', 'mines': 3, 'steps': 0, 'win_rate': 0, 'games_won': 0, 'games_lost': 0, 'type': ''}
RANDOM = 1
BFS = 2
CSP = 3
RL = 4


def test(width=8, height=8, mine=3, types=None):
    if types is None:
        types = [RANDOM, BFS, CSP, RL]
    statistic_list = []
    for type_i in types:
        num_games = 1
        won = 0
        steps = 0
        lost = 0
        for i in range(100):
            config = ms.GameConfig(width=width, height=height, num_mines=mine, auto_expand_clear_areas=False)
            if type_i == RANDOM:
                ai = ms.RandomAI()
                ai_type = 'random'
            elif type_i == BFS:
                ai = BreathFirstSearch((0, 0))
                ai_type = 'bfs'
            elif type_i == CSP:
                ai = CSP_agent(config, (0, 0))
                ai_type = 'csp'
            elif type_i == RL:
                ai = Reinforcement(config, (0, 0))
                ai_type = 'rl'
            result = ms.run_games(config, num_games, ai, None).pop()
            if result.victory:
                won += 1
                steps += result.num_moves
            else:
                lost += 1
        if won != 0:
            steps = int(steps / won)
        else:
            steps = 0
        statistic_list.append({'size': str(width) + '*' + str(height), 'mines': mine, 'steps': steps,
                               'win_rate': round(won / (won + lost), 2),
                               'games_won': won,
                               'games_lost': lost,
                               'type': ai_type})
    write_statistics_to_csv(statistic_list)


def write_statistics_to_csv(statistics_list):
    import csv
    csv_columns = list(statistics.keys())
    csv_file = "Statistics.csv"
    try:
        with open(csv_file, 'a+') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
            # writer.writeheader()
            for data in statistics_list:
                writer.writerow(data)
    except IOError:
        print("I/O error")


if __name__ == '__main__':
    test(width=8, height=8, mine=1)
    test(width=8, height=8, mine=2)
    test(width=8, height=8, mine=3)
    test(width=10, height=10, mine=5)
    test(width=10, height=10, mine=7)
    test(width=10, height=10, mine=10)
    test(width=16, height=16, mine=20)
    test(width=16, height=16, mine=30)
    test(width=16, height=16, mine=40)
