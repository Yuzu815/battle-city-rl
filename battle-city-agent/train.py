import random
import ray
from ray.rllib.models import ModelCatalog
from ray import air, tune
from ray.rllib.models.torch.fcnet import FullyConnectedNetwork as TorchFC
from ray.rllib.models.torch.torch_modelv2 import TorchModelV2
from ray.rllib.utils.framework import try_import_torch
from ray.tune.schedulers import PopulationBasedTraining

torch, nn = try_import_torch()


class TorchCustomModel(TorchModelV2, nn.Module):

    def __init__(self, obs_space, action_space, num_outputs, model_config, name):
        TorchModelV2.__init__(
            self, obs_space, action_space, num_outputs, model_config, name
        )
        nn.Module.__init__(self)

        self.torch_sub_model = TorchFC(
            obs_space, action_space, num_outputs, model_config, name
        )

    def forward(self, input_dict, state, seq_lens):
        input_dict["obs"] = input_dict["obs"].float()
        fc_out, _ = self.torch_sub_model(input_dict, state, seq_lens)
        return fc_out, []

    def value_function(self):
        return torch.reshape(self.torch_sub_model.value_function(), [-1])


if __name__ == "__main__":
    # local_mode
    ray.init(local_mode=True, dashboard_host='0.0.0.0')

    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--smoke-test", action="store_true", help="Finish quickly for testing"
    )
    args, _ = parser.parse_known_args()


    def explore(config):
        if config["train_batch_size"] < config["sgd_minibatch_size"] * 2:
            config["train_batch_size"] = config["sgd_minibatch_size"] * 2
        if config["num_sgd_iter"] < 1:
            config["num_sgd_iter"] = 1
        return config


    hyperparam_mutations = {
        "lambda": lambda: random.uniform(0.9, 1.0),
        "clip_param": lambda: random.uniform(0.01, 0.5),
        "lr": [1e-3, 5e-4, 1e-4, 5e-5, 1e-5],
        "num_sgd_iter": lambda: random.randint(1, 30),
        "sgd_minibatch_size": lambda: random.randint(64, 2048),
        "train_batch_size": lambda: random.randint(2000, 10000),
    }

    pbt = PopulationBasedTraining(
        time_attr="time_total_s",
        perturbation_interval=120,
        resample_probability=0.25,
        hyperparam_mutations=hyperparam_mutations,
        custom_explore_fn=explore,
    )

    stopping_criteria = {"training_iteration": 2000, "episode_reward_mean": 5}

    from env import TankEnv

    ModelCatalog.register_custom_model(
        "my_model", TorchCustomModel
    )

    tuner = tune.Tuner(
        "PPO",
        tune_config=tune.TuneConfig(
            metric="episode_reward_mean",
            mode="max",
            scheduler=pbt,
            num_samples=1 if args.smoke_test else 2,
        ),
        param_space={
            "env": TankEnv,
            "kl_coeff": 1.0,
            "num_workers": 4,
            "num_cpus": 1,
            "num_gpus": 0,
            "lambda": 0.95,
            "clip_param": 0.2,
            "model": {"dim": 780, "conv_filters": [[32, [4, 4], 2], [64, [4, 4], 2], [128, [8, 8], 2], [256, [16, 16], 2], [512, [49, 49], 1]]},
            "lr": 1e-4,
            "num_sgd_iter": tune.choice([10, 20, 30]),
            "sgd_minibatch_size": tune.choice([1]),
            "train_batch_size": tune.choice([1]),
            "framework": "torch",
        },
        run_config=air.RunConfig(
		stop=stopping_criteria,
		name="experiment_name",
        	local_dir="~/ray_results",
	),
    )
    results = tuner.fit()
