"""
Plan for this file.
    1. Create portfolio object from universe of presaved stocks
    2. Create agent objects
    3. Train agents.
    4. Test agent performance
"""

from experiments import *

import os
import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
matplotlib.use('Agg')
import datetime
from datetime import datetime as dt

from stable_baselines3 import A2C, DQN


def snp_stocks_basic():
    for i in range(0, len(SNP_500_TOP_100)):
        s = Stock(*SNP_500_TOP_100[i])
        s.extract_and_calculate_basic(verbose=False)
        s.calculate_cheat_values()
        save_stock(s, "data/snp_stocks_basic")
        print(s.code)

def snp_stocks_full():
    throttle = 60 * 7
    driver = Stock.get_google_news_driver(headless=False)
    for i in range(86, len(SNP_500_TOP_100)):
        s = Stock(*SNP_500_TOP_100[i], driver=driver)
        # s = Stock(*SNP_500_TOP_100[i])
        s.extract_and_calculate_all(verbose=False)
        save_stock(s, "data/snp_stocks_full")
        print(s.code)
        time.sleep(throttle)

def plots_and_stats(experiment_name, name_of_independent, folder, log_scale=True):    
    training_dict = {}
    testing_dict = {}
    for file in listdir(folder):
        if file == ".gitignore":
            continue
        file_name = file[:-5]
        components = file_name.split("_")
        period = components[-1]
        name = "_".join(components[:-1])
        file_path = f"{folder}/{file}"
        df = pd.read_excel(file_path, index_col=0)
        if period == "training":
            training_dict[name] = df
        elif period == "testing":
            testing_dict[name] = df
        else:
            raise ValueError("Neither training or testing")

    # Plot training
    for name in training_dict:
        # Calculate Averages
        df = training_dict[name]
        averages = []
        for y in range(len(df)):
            values = [df[x][y] for x in range(1,len(df.columns))]
            returns = [(v / 1_000_000) - 1 for v in values]
            average = sum(returns) / len(returns)
            averages.append(average)
        # Plot Averages
        plt.plot(averages, label=name)
    title = f"{experiment_name} Training"
    # plt.title(title)
    plt.xlabel("Episodes")
    plt.ylabel("Average Return")
    if log_scale: plt.yscale('log')
    plt.legend()
    plt.tight_layout()
    plt.savefig(f"data/plots/{title}")
    plt.clf()

    # Plot testing
    testing_stats = pd.DataFrame({"Agent": ["Average Return", "Std Devs", "Sample Size", "SM Std Devs", "Average Sharpe Ratio", "Sharpe Ration SM std Devs"]})
    average_final_values = []
    errs = []
    average_sharpe_ratio_values = []
    sr_errs = []
    names = []
    for name in testing_dict:
        df = testing_dict[name]
        values = [df[x][0] for x in range(1,len(df.columns))]
        returns = [(v / 1_000_000) - 1 for v in values]
        average = sum(returns) / len(returns)
        average_final_values.append(average)
        std_dev = np.std(returns)
        err = std_dev / math.sqrt(len(returns))
        errs.append(err)

        sharpe_ratios = [df[x][2] for x in range(1,len(df.columns))]
        average_sharpe_ratio = sum(sharpe_ratios) / len(sharpe_ratios)
        average_sharpe_ratio_values.append(average_sharpe_ratio)
        sr_err = np.std(sharpe_ratios) / math.sqrt(len(sharpe_ratios))
        sr_errs.append(sr_err)
        
        names.append(name)
        testing_stats[name] = [average, std_dev, len(returns), err, average_sharpe_ratio, sr_err]
    title = f"{experiment_name} Testing"
    # plt.title(title)
    if log_scale: plt.xscale('log')
    plt.barh(names, average_final_values, xerr=errs, ec="black", capsize=5)
    plt.xlabel("Average Return")
    plt.ylabel(name_of_independent)
    plt.tight_layout()
    plt.savefig(f"data/plots/{title}")
    plt.clf()
    title = f"{experiment_name} Testing Sharpe Ratios"
    # plt.title(title)
    if log_scale: plt.xscale('log')
    plt.barh(names, average_sharpe_ratio_values, xerr=sr_errs, ec="black", capsize=5)
    plt.xlabel("Average Sharpe Ratio")
    plt.ylabel(name_of_independent)
    plt.tight_layout()
    plt.savefig(f"data/plots/{title}")
    plt.clf()
    testing_stats.to_excel(f"data/testing_stats/{experiment_name}.xlsx")

if __name__ == "__main__":
    # snp_stocks_full()
    # experiment_1()
    # experiment_2()
    # experiment_3()
    # e3_sentiment_features()
    # e4_combined_features()
    # e4_2_combined_features_refined()
    e5_model_comparison()
    # plots_and_stats("Learning Rate Narrow Search", "Learning Rate", "data/results/learning_rate_narrow_search")
    # plots_and_stats("Learning Rate Broad Search", "Learning Rate", "data/results/learning_rate_broad_search")
    # plots_and_stats("Gamma Broad Search", "Gamma", "data/results/gamma_broad_search")
    # plots_and_stats("Technical Indicators Comparison", "Indicator", "data/results/technical_indicators", log_scale=False)
    # plots_and_stats("Raw sent", "Feature", "data/results/raw_sentiment_features", log_scale=False)
    # plots_and_stats("Combined Features", "Feature", "data/results/combined_features", log_scale=False)
    plots_and_stats("Combined Features Refined", "Feature", "data/results/combined_features_refined", log_scale=False)


    # stocks = retrieve_stocks_from_folder("data/snp_stocks_full")
    # print(stocks[0].df.columns)
    # stocks_50 = [s for s in stocks if s.code in [sa[1] for sa in SNP_500_TOP_100[:50]]]
    # for s in stocks_50:
    #     print(s.code)
    #     save_stock(s, "data/snp_50_stocks_full")


    # print(len(stocks_50))
    # for s in stocks:
    #     print(s.code)