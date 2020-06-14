import numpy as np
import sys
import os

from gensim.models.wrappers import FastText
import tensorflow as tf
from keras.backend.tensorflow_backend import set_session
from keras.models import load_model

import re


class IntentAnalyzer:
    def __init__(self):
        self.model_ft = FastText.load_fasttext_format('PATH_model_drama.bin')

        self.config = tf.ConfigProto()
        self.config.gpu_options.per_process_gpu_memory_fraction = 0.01
        set_session(tf.Session(config=self.config))


        self.model_fci  = load_model('PATH_rec_self_char_dense_drop-24-0.8882.hdf5')

        self.wdim=100

        self.regex = re.compile(r'.*[?]([-=+,#/;:\\^$.@*\s\'\"~%&!\(\)\<\>])*$')

    def featurize_charrnn_utt(self, corpus,maxcharlen):
        rec_total = np.zeros((1,maxcharlen, self.wdim))
        s = corpus
        for j in range(len(s)):
                if s[-j-1] in self.model_ft and j<maxcharlen:
                    rec_total[0,-j-1,:]=self.model_ft[s[-j-1]]
        return rec_total

    def pred_only_text(self, s):
        rec = self.featurize_charrnn_utt(s, 80)
        att=np.zeros((1,64))
        z = self.model_fci.predict([rec,att])[0]
        z = np.argmax(z)
        y = int(z)
        return z


    def is_question(self, s):
        m = self.regex.match(s)
        if m:
            return True
        else:
            if self.pred_only_text(s) == 2:
                return True
            else:
                return False
