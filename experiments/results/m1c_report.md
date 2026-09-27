# M1c — per-batch optimality gap (greedy objective − optimal objective)

| drivers | arm | gap s / batch | gap % of objective | batches where greedy is worse | riders / batch |
|---|---|---|---|---|---|
| 250 | optimal@10s plain vs global_greedy | 3.8 | 0.01 | 6.6% | 39.9 |
| 300 | optimal@10s plain vs global_greedy | 14.0 | 0.14 | 16.4% | 13.5 |
| 350 | optimal@10s plain vs global_greedy | 7.5 | 0.85 | 11.3% | 3.6 |
| 400 | optimal@10s plain vs global_greedy | 1.5 | 0.31 | 4.8% | 3.6 |
| 250 | optimal@10s aware(V=900) vs global_greedy | 3.7 | 0.01 | 4.8% | 43.0 |
| 300 | optimal@10s aware(V=900) vs global_greedy | 11.4 | 0.06 | 10.3% | 24.3 |
| 350 | optimal@10s aware(V=900) vs global_greedy | 12.3 | 0.40 | 11.5% | 6.5 |
| 400 | optimal@10s aware(V=900) vs global_greedy | 3.4 | 0.55 | 5.2% | 3.7 |
| 250 | optimal@10s plain vs fifo_greedy | 710.3 | 2.09 | 87.3% | 39.9 |
| 300 | optimal@10s plain vs fifo_greedy | 346.5 | 3.41 | 58.8% | 13.5 |
| 350 | optimal@10s plain vs fifo_greedy | 20.5 | 2.27 | 17.5% | 3.6 |
| 400 | optimal@10s plain vs fifo_greedy | 3.8 | 0.77 | 6.9% | 3.6 |
| 250 | optimal@10s aware(V=900) vs fifo_greedy | 588.4 | 1.60 | 82.9% | 43.0 |
| 300 | optimal@10s aware(V=900) vs fifo_greedy | 461.8 | 2.30 | 70.9% | 24.3 |
| 350 | optimal@10s aware(V=900) vs fifo_greedy | 95.2 | 2.58 | 28.9% | 6.5 |
| 400 | optimal@10s aware(V=900) vs fifo_greedy | 8.3 | 1.21 | 8.1% | 3.7 |
