import numpy as np
from copy import deepcopy
from .decorator import save_to_json, load_from_json


DEFAULT_NAME = '_feature_default_name_'


class RulesMixin:
    _rules = {}

    def _parse_rule(self, rule):
        return rule
    
    def _format_rule(self, rule):
        return rule
    
    def default_rule(self):
        return self._rules[DEFAULT_NAME]
    
    @property
    def _default_name(self):
        return DEFAULT_NAME

    @property
    def rules(self):
        return self._rules
    
    @rules.setter
    def rules(self, value):
        self._rules = value
    

    @load_from_json(is_class = True, require_first = True)
    def load(self, rules, update = False, **kwargs):
        rules = deepcopy(rules)

        if not isinstance(rules, dict):
            rules = {
                DEFAULT_NAME: rules,
            }
        
        for key in rules:
            rules[key] = self._parse_rule(rules[key])
        
        if update:
            self._rules.update(rules)
        else:
            self._rules = rules
        
        return self
    
    @save_to_json(is_class = True)
    def export(self, **kwargs):
        res = {}
        for key in self._rules:
            res[key] = self._format_rule(self._rules[key], **kwargs)
        
        return res
    
    def update(self, *args, **kwargs):
        return self.load(*args, update = True, **kwargs)
    

    def __len__(self):
        return len(self._rules.keys())
    
    def __contains__(self, key):
        return key in self._rules
    
    def __getitem__(self, key):
        return self._rules[key]
    
    def __setitem__(self, key, value):
        self._rules[key] = value





RE_NUM = r'-?\d+(.\d+)?'
RE_SEP = r'[~-]'
RE_BEGIN = r'(-inf|{num})'.format(num = RE_NUM)
RE_END = r'(inf|{num})'.format(num = RE_NUM)
RE_RANGE = r'\[{begin}\s*{sep}\s*{end}\)'.format(
    begin = RE_BEGIN,
    end = RE_END,
    sep = RE_SEP,
)





class BinsMixin:
    EMPTY_BIN = -1
    ELSE_GROUP = 'else'

    @classmethod
    def parse_bins(self, bins):

        if self._is_numeric(bins):
            return self._numeric_parser(bins)
        
        l = list()

        for item in bins:
            if item == self.ELSE_GROUP:
                l.append(item)
            else:
                l.append(item.split(','))

        return np.array(l)


    @classmethod
    def format_bins(self, bins, index = False):
        l = list()

        if np.issubdtype(bins.dtype, np.number):
            has_empty = len(bins) > 0 and np.isnan(bins[-1])
            
            if has_empty:
                bins = bins[:-1]
            
            sp_l = [-np.inf] + bins.tolist() + [np.inf]
            for i in range(len(sp_l) - 1):
                l.append('['+str(sp_l[i])+' ~ '+str(sp_l[i+1])+')')
            
            if has_empty:
                l.append('nan')
        else:
            for keys in bins:
                if isinstance(keys, str) and keys == self.ELSE_GROUP:
                    l.append(keys)
                else:
                    l.append(','.join(keys))

        if index:
            indexes = [i for i in range(len(l))]
            l = ["{}.{}".format(ix, lab) for ix, lab in zip(indexes, l)]

        return np.array(l)
    

    @classmethod
    def _is_numeric(self, bins):
        m = exp.match(bins[0])

        return m is not None
    
    @classmethod
    def _numeric_parser(self, bins):
        l = list()

        for item in bins:

            if item == 'nan':
                l.append(np.nan)
                continue
            
            m = exp.match(item)
            split = m.group(3)

            if split == 'inf':
                # split = np.inf
                continue
            
            split = float(split)

            l.append(split)
        
        return np.array(l)