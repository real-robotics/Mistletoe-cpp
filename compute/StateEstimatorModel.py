from rknnlite.api import RKNNLite

class StateEstimatorModel:
    def __init__(self, model_path) -> None:
        self.rknn_lite = RKNNLite()
        ret = self.rknn_lite.load_rknn(model_path)
        ret = self.rknn_lite.init_runtime(core_mask=RKNNLite.NPU_CORE_0)

        # Load the RKNN model
        if ret != 0:
            print(f"Failed to load RKNN model. Error code: {ret}")
            exit(ret)

    # takes a list of 45 items that includes the following in this specific order:
    # base_ang_vel, projected_gravity, velocity command of size 3
    # joint pos,vel,action of size 12
    # returns 3d lin vel of base 
    
    def compute_lin_vel(self, obs):
        outputs = self.rknn_lite.inference(inputs=obs)
        return outputs