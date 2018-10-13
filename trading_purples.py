
### IMPORTS ###
import random
import sys, os
from functools import partial
from itertools import product

# Libs
import numpy as np
from hist_service import HistWorker
from crypto_evolution import CryptoFolio
# Local
import neat.nn
import _pickle as pickle
from pureples.shared.substrate import Substrate
from pureples.shared.visualize import draw_net
from pureples.es_hyperneat.es_hyperneat import ESNetwork
# Local
class PurpleTrader:
    
    #needs to be initialized so as to allow for 62 outputs that return a coordinate

    # ES-HyperNEAT specific parameters.
    params = {"initial_depth": 0, 
            "max_depth": 1, 
            "variance_threshold": 0.03, 
            "band_threshold": 0.3, 
            "iteration_level": 1,
            "division_threshold": 0.5, 
            "max_weight": 5.0, 
            "activation": "sigmoid"}

    # Config for CPPN.
    config = neat.config.Config(neat.genome.DefaultGenome, neat.reproduction.DefaultReproduction,
                                neat.species.DefaultSpeciesSet, neat.stagnation.DefaultStagnation,
                                'config_trader')
                                
    start_idx = 0
    highest_returns = 0
    portfolio_list = []

    in_shapes = []
    out_shapes = []
    def __init__(self):
        self.hs = HistWorker()
        self.end_idx = len(self.hs.currentHists["DASH"])
        self.but_target = .1
        self.inputs = self.hs.hist_shaped.shape[0]*self.hs.hist_shaped[0].shape[1]
        self.outputs = self.hs.hist_shaped.shape[0]
        for ix in range(self.outputs):
            self.out_shapes.append((0, ix))
            for ix2 in range(len(self.hs.hist_shaped[0][0])):
                self.in_shapes.append((ix, ix2))
        #self.subStrate = Substrate()
        
        
    def set_portfolio_keys(self, folio):
        for k in self.hs.currentHists.keys():
            folio.ledger[k] = 0

    def get_one_bar_input_2d(self, end_idx):
        active = {}
        for x in range(0, self.outputs):
            active[x] = self.hs.hist_shaped[x][end_idx]
        return active

    def evaluate(self, network, verbose=False):
        portfolio = CryptoFolio(1)
        active = {}
        result = {}
        if not isinstance(network, NeuralNetwork):
            network = NeuralNetwork(network)
        for z in range(0, 14):
            '''
            if(z == 0):
                old_idx = 1
            else:
                old_idx = z * 5
            new_idx = (z + 1) * 5
            '''
            active = self.get_one_bar_input_2d(z)
            results[z] = network.feed(active)
        #first loop sets up buy sell hold signal result from the net,
        #we want to gather all 14 days of 
        for i in range(0, 14):
            out = results[i]
            for x in range(0, self.outputs):
                sym = self.hs.coin_dict[x]
                if(out[x] == 1.0):
                    portfolio.buy_coin(sym, self.hs.currentHists[sym][x]['close'])
                elif(out[x] == 0.0):
                    portfolio.sell_coin(sym)
                #skip the hold case because we just dont buy or sell hehe
        end_ts = self.hs.hist_shaped[0][14][0]
        result_val = portfolio.get_total_btc_value(int(end_ts))
        print(results)
        if(results > self.highest_returns):
            self.highest_returns = results
        return results

    def solve(self, network):
        return self.evaluate(network) >= self.highest_returns
        
if __name__ == '__main__':
    task = PurpleTrader()
    print(task.inputs)
    print(task.outputs)
    print(task.out_shapes)
    print(task.in_shapes)
    print(task.get_one_bar_input_2d(0))
    '''
    for x in range(len(task.hs.hist_shaped[0])):
        print(task.hs.hist_shaped[1][x][3],task.hs.hist_shaped[0][x][3])
    '''
    