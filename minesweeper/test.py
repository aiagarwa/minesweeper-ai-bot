import logging
import minesweeper as ms
from bfs import BreathFirstSearch
from csp import CSP_agent
from RL import Reinforcement

statistics = {'size': '8 * 8', 'mines': 3, 'win_rate': 0, 'games_won': 0, 'games_lost': 0, 'type': ''}


def test(width=8, height=8, mine=3):
    # 10 mines on 8 * 8
    num_games = 1
    bfs_won = 0
    bfs_lost = 0
    csp_won = 0
    csp_lost = 0
    rl_won = 0
    rl_lost = 0
    for i in range(100):
        config = ms.GameConfig(width=width, height=height, num_mines=mine, auto_expand_clear_areas=False)
        result_bfs = ms.run_games(config, num_games, BreathFirstSearch((3, 3)), None).pop()
        if result_bfs.victory:
            bfs_won += 1
        else:
            bfs_lost += 1
        result_csp = ms.run_games(config, num_games, CSP_agent(config, (3, 3)), None).pop()
        if result_csp.victory:
            csp_won += 1
        else:
            csp_lost += 1
        result_rl = ms.run_games(config, num_games, Reinforcement(config, (3, 3)), None).pop()
        if result_rl.victory:
            rl_won += 1
        else:
            rl_lost += 1
    statistics_bfs = {'size': str(width) + '*' + str(height), 'mines': mine, 'win_rate': 0, 'games_won': bfs_won,
                      'games_lost': bfs_lost,
                      'type': 'bfs'}
    statistics_csp = {'size': str(width) + '*' + str(height), 'mines': mine, 'win_rate': 0, 'games_won': csp_won,
                      'games_lost': csp_lost,
                      'type': 'csp'}
    statistics_rl = {'size': str(width) + '*' + str(height), 'mines': mine, 'win_rate': 0, 'games_won': rl_won,
                     'games_lost': rl_lost,
                     'type': 'rl'}
    gather_statistics(statistics_bfs, statistics_csp, statistics_rl)


def gather_statistics(statistics_bfs, statistics_csp, statistics_rl):
    statistics_bfs['win_rate'] = statistics_bfs["games_won"] / (
            statistics_bfs["games_won"] + statistics_bfs["games_lost"])
    statistics_csp['win_rate'] = statistics_csp["games_won"] / (
            statistics_csp["games_won"] + statistics_csp["games_lost"])
    statistics_rl['win_rate'] = statistics_rl["games_won"] / (
            statistics_rl["games_won"] + statistics_rl["games_lost"])
    statistics_list = [statistics_bfs, statistics_csp, statistics_rl]
    write_statistics_to_csv(statistics_list)


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
    test(width=8, height=8, mine=3)
    test(width=10, height=10, mine=5)
    test(width=10, height=10, mine=7)
    test(width=10, height=10, mine=10)
    test(width=16, height=16, mine=20)
    test(width=16, height=16, mine=30)
    test(width=16, height=16, mine=40)
