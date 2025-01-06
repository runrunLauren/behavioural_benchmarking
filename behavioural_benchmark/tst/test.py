from behavioural_benchmark.stn import StnPy
import pandas as pd
import time

def check_correctness():
    STN_R_values = pd.read_csv("resources/stnpy/STN_R_easy_results.csv")
    g = StnPy("resources/stnpy/easy.txt")
    g.get_data(delimiter=",")
    g.create_stn(best_fit=0, use_best_fit_delta=False)
    assert g.get_ntotal() == STN_R_values.loc[0]["ntotal"]
    assert g.get_etotal() == STN_R_values.loc[0]["etotal"]
    assert g.get_nbest() == STN_R_values.loc[0]["nend"]
    assert g.get_nend() == STN_R_values.loc[0]["nend"]
    assert round(g.get_best_strength(), 4) == STN_R_values.loc[0]["best-strength"]
    assert g.get_components() == STN_R_values.loc[0]["components"]
    assert g.get_plength() == STN_R_values.loc[0]["plength"]
    assert g.get_altered_nshared() == 5
    print("Correctness tests passed")

    # I've tested the STN R package and I disagree with it's output for npaths. It uses a distance matrix to calculate
    # the number of paths, but this is incorrect - it can at most count one path per starting node,  even if there are
    # many
    # assert g.get_npaths() == STN_R_values.loc[0]["npaths"]


def run_one_run():
    g = StnPy("resources/stnpy/easy.txt")
    g.get_data(delimiter=",", run_numbers=[1])
    g.create_stn(best_fit=0, use_best_fit_delta=False)
    print("ntotal: ", g.get_ntotal(), ", etotal: ", g.get_etotal(), ", nbest: ", g.get_nbest(),
          ", nend: ", g.get_nend(), ", best-strength: ", g.get_best_strength(), ", components: ", g.get_components(),
          ", npaths: ", g.get_npaths(), ", plength: ", g.get_plength(), ", nshared: ", g.get_altered_nshared())


def run_two_runs():
    g = StnPy("resources/stnpy/easy.txt")
    g.get_data(delimiter=",", run_numbers=[1, 3])
    g.create_stn(best_fit=0, use_best_fit_delta=False)
    print("ntotal: ", g.get_ntotal(), ", etotal: ", g.get_etotal(), ", nbest: ", g.get_nbest(),
          ", nend: ", g.get_nend(), ", best-strength: ", g.get_best_strength(), ", components: ", g.get_components(),
          ", npaths: ", g.get_npaths(), ", plength: ", g.get_plength(), ", nshared: ", g.get_altered_nshared())


def run_big_file():
    g = StnPy("resources/stnpy/stn.csv")
    g.get_data(delimiter=",", run_numbers=[1, 2])
    g.create_stn(best_fit=0, use_best_fit_delta=True)
    print("ntotal: ", g.get_ntotal(), ", etotal: ", g.get_etotal(), ", nbest: ", g.get_nbest(),
          ", nend: ", g.get_nend(), ", best-strength: ", g.get_best_strength(), ", components: ", g.get_components(),
          ", npaths: ", g.get_npaths(), ", plength: ", g.get_plength(), ", nshared: ", g.get_altered_nshared())


if __name__ == '__main__':
    check_correctness()
    run_one_run()
    run_two_runs()
    start = time.time()
    run_big_file()
    end = time.time()
    print("time: ", end - start)