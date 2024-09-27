from rknnlite.api import RKNNLite

import numpy as np

class PPOPolicy:
    def __init__(self, model_path) -> None:
        self.rknn_lite = RKNNLite()
        ret = self.rknn_lite.load_rknn(model_path)
        ret = self.rknn_lite.init_runtime(core_mask=RKNNLite.NPU_CORE_0)

        # Load the RKNN model
        if ret != 0:
            print(f"Failed to load RKNN model. Error code: {ret}")
            exit(ret)
    
    def predict(self, obs):

        # weird behavior where if tolist() is run once, then it stays as a list 
        action = self.rknn_lite.inference(inputs=obs)

        # idrk whats going on here but its like weird formatting bs
        if (type(action) != list):
            action = action.flatten().tolist()
            return action
        else:
            action = action[0].flatten().tolist()
            return action