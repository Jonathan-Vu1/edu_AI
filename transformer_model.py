import torch.nn as nn
import torch.nn.functional as F
import torch

class TransformerModel(nn.Module):
    def __init__(self, num_tokens, d_model, nhead, num_encoder_layers, num_decoder_layers, dim_feedforward, max_seq_length, dropout = 0.1):

        # Create transformer model, add embedding, normalization, Linear output
        super(TransformerModel, self).__init__()
        self.embedding = nn.Embedding(num_tokens, d_model)
        self.positional_encoding = nn.Parameter(torch.zeros(1, max_seq_length, d_model))
        self.transformer = nn.Transformer(
            d_model = d_model,
            nhead = nhead,
            num_encoder_layers = num_encoder_layers,
            num_decoder_layers = num_decoder_layers,
            dim_feedforward = dim_feedforward,
            dropout = dropout,
            batch_first = True
        )
        self.layer_norm = nn.LayerNorm(d_model)
        self.out = nn.Linear(d_model, num_tokens)
        self.max_seq_length = max_seq_length

    def forward(self, src, tgt):

        # Ensure correct sizes
        src_seq_length = src.size(1)
        tgt_seq_length = tgt.size(1)

        # Use layer norm w/embedding and positional encoding
        src = self.layer_norm(self.embedding(src) + self.positional_encoding[:, :src_seq_length, :])
        tgt = self.layer_norm(self.embedding(tgt) + self.positional_encoding[:, :tgt_seq_length, :])

        # Use mask for correct sizing
        tgt_mask = self.transformer.generate_square_subsequent_mask(tgt.size(1)).to(tgt.device)
        tgt_mask = tgt_mask.to(torch.bool)

        # Pass through transformer and return output
        output = self.transformer(src, tgt, tgt_mask= tgt_mask)
        output = self.out(output)

        return output