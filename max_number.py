import heapq
def top_max(nums,k):
  counter={}
  for num in nums:
    counter[num] = counter.get(num,0) + 1

  heap = [(-count,num) for num,count in counter.items()]
  heapq.heapify(heap)
  return [heapq.heappop(heap)[1] for _ in range(k)]

if __name__=='__main__':
    print(top_max([1,2,3,4,2,2,4,4,100,100,100,100,100,4,4,1,1],2))
