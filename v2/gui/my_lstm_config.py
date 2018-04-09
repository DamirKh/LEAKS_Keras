from lstm_config_dialog import lstm_config_dialog


class MyLstmConfigDialog(lstm_config_dialog):

    def P_activation(self, event):
        a = self._activation
        if event.Int == 1:
            a.Enable(True)
        if event.Int == 0:
            a.SetSelection(a.FindString('tanh'))
            a.Enable(False)
        pass

    def P_recurrent_activation(self, event):
        r = self._recurrent_activation
        if event.Int == 1:
            r.Enable(True)
        if event.Int == 0:
            r.SetSelection(r.FindString('hard_sigmoid'))
            r.Enable(False)

    def P_use_bias_bool(self, e):
        if e.Int:
            self._use_bias.Enable()
        else:
            self._use_bias.Enable(False)

    def P_kernel_initializer_bool(self, e):
        if e.Int:
            self._kernel_initializer.Enable()
        else:
            self._kernel_initializer.Enable(False)

    def P_return_sequences_bool(self, e):
        if e.Int:
            self._return_sequences.Enable()
        else:
            self._return_sequences.Enable(False)

    def P_stateful_bool(self, e):
        if e.Int:
            self._stateful.Enable()
        else:
            self._stateful.Enable(False)
