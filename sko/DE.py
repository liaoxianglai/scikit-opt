#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2019/8/20
# @Author  : github.com/guofei9987


import numpy as np
from .base import SkoBase
from abc import ABCMeta, abstractmethod
from .operators import crossover, mutation, ranking, selection
from .GA import GeneticAlgorithmBase, GA


class DifferentialEvolutionBase(SkoBase, metaclass=ABCMeta):
    pass


class DE(GeneticAlgorithmBase):
    def __init__(self, func, n_dim, F=0.5,
                 size_pop=50, max_iter=200, prob_mut=0.3,
                 lb=-1, ub=1,
                 constraint_eq=[], constraint_ueq=[]):
        super().__init__(func, n_dim, size_pop, max_iter, prob_mut,
                         constraint_eq=constraint_eq, constraint_ueq=constraint_ueq)

        self.F = F
        self.V = None
        self.U = None
        self.lb, self.ub = np.array(lb) * np.ones(self.n_dim), np.array(ub) * np.ones(self.n_dim)
        self.crtbp()

    def crtbp(self):
        # create the population
        self.X = np.random.uniform(low=self.lb, high=self.ub, size=(self.size_pop, self.n_dim))
        return self.X

    def chrom2x(self):
        pass

    def ranking(self):
        pass

    def mutation(self):
        '''
        V[i]=X[r1]+F(X[r2]-X[r3]),
        where i, r1, r2, r3 are randomly generated
        '''
        X = self.X
        random_idx = np.random.randint(0, self.size_pop, size=(self.size_pop, 4))

        # 这里还少一个逻辑：i, r1, r2, r3各不相等
        i, r1, r2, r3 = random_idx[:, 0], random_idx[:, 1], random_idx[:, 2], random_idx[:, 3]

        # 这里少个逻辑，i，但想来应该是差不多的（没细想）
        # 这里还少一个逻辑，F，这里用固定值，为了防止早熟，可以用自适应值
        self.V = X[r1, :] + self.F * (X[r2, :] - X[r3, :])

        # the lower & upper bound still works
        mask = np.random.uniform(low=self.lb, high=self.ub, size=(self.size_pop, self.n_dim))
        self.V = np.where(self.V < self.lb, mask, self.V)
        self.V = np.where(self.V > self.ub, mask, self.V)
        return self.V

    def crossover(self):
        '''
        if rand < prob_crossover use V, else use X
        '''
        mask = np.random.rand(self.size_pop, self.n_dim) < self.prob_mut
        self.U = np.where(mask, self.V, self.X)
        return self.U

    def selection(self):
        '''
        greedy selection
        '''
        X = self.X.copy()
        f_X = self.x2y().copy()
        self.X = U = self.U
        f_U = self.x2y()

        self.X = np.where((f_X < f_U).reshape(-1, 1), X, U)
        return self.X

    def run(self, max_iter=None):
        self.max_iter = max_iter or self.max_iter
        for i in range(self.max_iter):
            self.mutation()
            self.crossover()
            self.selection()

            # record the best ones
            generation_best_index = self.Y.argmin()
            self.generation_best_X.append(self.X[generation_best_index, :])
            self.generation_best_Y.append(self.Y[generation_best_index])
            self.all_history_Y.append(self.Y)

        global_best_index = np.array(self.generation_best_Y).argmin()
        global_best_X = self.generation_best_X[global_best_index]
        global_best_Y = self.func(global_best_X)
        return global_best_X, global_best_Y
