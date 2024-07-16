from rknnlite.api import RKNNLite

class PPOActorModel:
    def __init__(self, model_path) -> None:
        self.rknn_lite = RKNNLite()
        ret = self.rknn_lite.load_rknn(model_path)
        ret = self.rknn_lite.init_runtime(core_mask=RKNNLite.NPU_CORE_0)

        # Load the RKNN model
        if ret != 0:
            print(f"Failed to load RKNN model. Error code: {ret}")
            exit(ret)
    
    def compute_joint_pos(self, obs):
        joint_pos = self.rknn_lite.inference(inputs=obs)
        return joint_pos
