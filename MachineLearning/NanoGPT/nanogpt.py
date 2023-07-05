import torch
import torch.nn as nn
from torch.nn import functional as F

batch_size = 32
block_size = 8
max_iters = 10000
eval_interval = 200
learning_rate = 0.02
device = 'cuda' if torch.cuda.is_available() else 'cpu'
eval_iters = 200
n_embed = 32 
# -----------------------------------------------------------------------------------------------
torch.manual_seed(1337)

with open('input.txt','r',encoding='utf-8') as f: # load the data 
  text = f.read()

chars = sorted(list(set(text)))                                                 # Extract the  unique characters from the text
vocab_size = len(chars)                                                         # Size of the vocabulary (in this case the unique characters)
# print(''.join(chars))
# print(vocab_size)                                                               # print the vocabulary

#tokenize the input text 
stoi = {ch:i for i,ch in enumerate(chars)} # from strings to integers 
itos = {i:ch for i,ch in enumerate(chars)} # from integers to strings 
encode = lambda s: [stoi[c] for c in s]
decode = lambda l: ''.join([itos[i] for i in l])

data = torch.tensor(encode(text), dtype = torch.long)                           # encode all the text and assign the tokens to a tensor 
n = int(0.9*len(data))
train_data = data[:n]
val_data = data[n:]

def get_batch(split):
  data = train_data if split == 'train' else val_data                           # select the training or the validation set
  ix = torch.randint(len(data) - block_size, (batch_size,))                     # random token 
  x = torch.stack([data[i:i+block_size] for i in ix])                           # select words in n postions  
  y = torch.stack([data[i+1:i+block_size+1] for i in ix])                       # select words in n+1 positions
  x, y = x.to(device), y.to(device)
  return x,y

@torch.no_grad()
def estimate_loss():
  out = {}
  model.eval()
  for split in ['train','val']:
    losses = torch.zeros(eval_iters)
    for k in range(eval_iters):
      X, Y = get_batch(split)
      logits, loss = model(X,Y)
      losses[k] = loss.item()
    out[split] = losses.mean()
  model.train()
  return out

class Head(nn.Module):
  """one head self attention"""

  def __init__(self, head_size):
    super().__init__()
    self.key = nn.Linear(n_embed, head_size, bias=False)
    self.query = nn.Linear(n_embed, head_size, bias=False)
    self.value = nn.Linear(n_embed, head_size, bias=False)
    self.register_buffer('tril', torch.tril(torch.ones(block_size,block_size)))

  def forward(self,x):
    B,T,C = x.shape
    k = self.key(x)
    q = self.query(x)

    wei = q @ k.transpose(-2,-1) * C**-0.5
    wei = wei.masked_fill(self.tril[:T,:T] == 0, float('-inf'))
    wei = F.softmax(wei, dim=1)

    v = self.value(x)
    out = wei @ v 
    return out 

class MultiHeadAttention(nn.Module):

  def __init__(self, num_heads, head_size):
    super().__init__()
    self.heads = nn.ModuleList([Head(head_size) for _ in range(num_heads)])

  def forward(self,x): 
    return torch.cat([h(x) for h in self.heads],dim=-1)

class FeedForward(nn.Module):
  def __init__(self, n_embed):
    super().__init__()
    self.net = nn.Sequential(
      nn.Linear(n_embed,n_embed),
      nn.ReLU(),
    )

  def forward(self,x):
    return self.net(x)
  

# Create the language model 
class BigramLanguageModel(nn.Module):
  def __init__(self):
    super().__init__()
    ## create the embeddings 
    self.token_embedding_table = nn.Embedding(vocab_size, n_embed)           # returns a tensor (shape of input, shape of vocab)
    self.position_embedding_table = nn.Embedding(block_size, n_embed)
    self.sa_heads = MultiHeadAttention(4,n_embed//4)
    self.ffwd = FeedForward(n_embed)
    self.lm_head = nn.Linear(n_embed,vocab_size)

  def forward(self,idx,targets=None): 
    B, T = idx.shape

    tok_embds = self.token_embedding_table(idx)
    # create the poitional embenddings from 0 to T-1 
    pos_embed = self.position_embedding_table(torch.arange(T,device=device))
    x = tok_embds + pos_embed
    x = self.sa_heads(x)
    x = self.ffwd(x)
    logits = self.lm_head(x)

    if targets is None:
      loss = None
    else:
      logits = torch.permute(logits,(0,2,1))
      loss = F.cross_entropy(logits, targets)
    return logits, loss


  def generate(self,idx,max_new_tokens):
    for _ in range(max_new_tokens):
      idx_cond = idx[:,-block_size:]
      logits, loss = self(idx_cond)
      logits = logits[:,-1,:]
      probs = F.softmax(logits,dim=-1)

      idx_next = torch.multinomial(probs,num_samples=1)
      idx = torch.cat((idx,idx_next),dim=1)
    
    return idx
    
# ----------------------------------------------------------------------------------------
model = BigramLanguageModel()
m = model.to(device)

optimizer = torch.optim.AdamW(model.parameters(), lr=learning_rate)

for iter in range(max_iters):

  if iter % eval_interval == 0:
    losses = estimate_loss()
    print(f"step {iter}: train loss {losses['train']:.4f}, val loss {losses['val']:.4f}")

    xb, yb = get_batch('train')

    logits, loss = model(xb,yb)
    optimizer.zero_grad(set_to_none = True)
    loss.backward()
    optimizer.step()


context = torch.zeros((1,1), dtype=torch.long, device=device)
print(decode(m.generate(context,max_new_tokens=300)[0].tolist()))


