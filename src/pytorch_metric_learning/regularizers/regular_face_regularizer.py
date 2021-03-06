from .base_regularizer import BaseRegularizer
import torch
from ..utils import common_functions as c_f
from ..distances import CosineSimilarity

# modified from http://kaizhao.net/regularface
class RegularFaceRegularizer(BaseRegularizer):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        assert self.distance.is_inverted

    def compute_loss(self, weights):
        dtype, device = weights.dtype, weights.device
        num_classes = weights.size(0)
        cos = self.distance(weights)
        cos1 = cos.clone()
        with torch.no_grad():
            cos1.fill_diagonal_(c_f.neg_inf(dtype))
            _, indices = self.distance.smallest_dist(cos1, dim=1)
            mask = torch.zeros((num_classes, num_classes), dtype=dtype).to(device)
            row_nums = torch.arange(num_classes).long().to(device)
            mask[row_nums, indices] = 1
        losses = torch.sum(cos*mask, dim=1)
        return {"loss": {"losses": losses, "indices": c_f.torch_arange_from_size(weights), "reduction_type": "element"}}

    def get_default_distance(self):
        return CosineSimilarity()