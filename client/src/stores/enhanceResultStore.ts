import { defineStore } from 'pinia';

type EnhanceResultState = {
   lr: string | undefined;
   sr: string | undefined;
};

export const useEnhanceResultStore = defineStore('enhance-result', {
   state: (): { enhanceResultState: EnhanceResultState } => {
      const storedEnhanceResultState =
         localStorage.getItem('enhanceResultState');

      return {
         enhanceResultState: storedEnhanceResultState
            ? JSON.parse(storedEnhanceResultState)
            : {
                 lr: null,
                 sr: null,
              },
      };
   },

   actions: {
      setEnhanceResultState(state: EnhanceResultState) {
         this.enhanceResultState = state;
         localStorage.setItem(
            'enhanceResultState',
            JSON.stringify(this.enhanceResultState)
         );
      },

      clearState() {
         this.enhanceResultState = {
            lr: undefined,
            sr: undefined,
         };
         localStorage.removeItem('enhanceResultState');
      },
   },
});
