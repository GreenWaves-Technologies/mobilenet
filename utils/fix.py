import torch

class Tile(torch.nn.Module):
    def __init__(self, tile_size=(10, 10)):
        super().__init__()
        self.unfold = torch.nn.Unfold(
            kernel_size=tile_size,
            stride=tile_size
        )
        self.tile_size = tile_size

    def forward(self, x):
        batch_size, num_channels, H, W = x.shape
        x = self.unfold(x)
        x = x.view(batch_size, num_channels, *self.tile_size, x.shape[-1])
        x = x.transpose(-1, 2).transpose(1,2)
        return x

class Untile(torch.nn.Module):
    def __init__(self, output_size, tile_size=(10, 10)):
        super().__init__()
        self.fold = torch.nn.Fold(
            output_size=output_size,
            kernel_size=tile_size,
            stride=tile_size
        )
        self.output_size = output_size
        self.tile_size = tile_size

    def forward(self, y):
        batch_size, num_blocks, num_channels, blockH, blockW = y.shape
        y = y.transpose(2,1).transpose(-1, 2)
        #batch_size, num_channels, blockH, blockW, num_blocks = y.shape
        y = y.reshape(batch_size, num_channels*blockH*blockW, num_blocks)
        y = self.fold(y)
        return y
    
class Fixer(torch.nn.Module):
    def __init__(self):
        super().__init__()
        self.untile = Untile((28,28), tile_size=(3,3))
        self.tile = Tile(tile_size=(9,9))

    #hid is bs nc h w
    def forward(self, hid):
        B, C, H, W = hid.shape
        hid = self.tile(hid) #B NT C ts ts = 1 9 32 9 9
        hid = hid.reshape(1, 3, 3, C, -1)
        hid = hid.permute(0, 4, 3, 1, 2)
        hid = self.untile(hid)
        return hid

