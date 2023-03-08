import bisect
import sys
import heapq as hq


class Process:
    def __init__(self, pid, arrival_time, burst_time):
        self.pid = pid
        self.arrival_time = arrival_time
        self.burst_time = burst_time

    def __lt__(self, other):
        return self.burst_time < other.burst_time


def main():
    sorted_pids, process_completion_times = [], []
    process_arrival_times, process_burst_times = [], []
    processes = []

    def parse_batchfile(batchfile_data):
        pids, process_arrival_times, process_burst_times = [], [], []
        for line in batchfile_data:
            processes.append([int(x.strip()) for x in line.split(',')])
        processes.sort(key=lambda x: x[1])  # Sort by arrival time
        for process in processes:
            pids.append(process[0])
            process_arrival_times.append(process[1])
            process_burst_times.append(process[2])
        return pids, process_arrival_times, process_burst_times

    # Check if the correct number of arguments have been provided
    if len(sys.argv) != 3:
        print("""Please provide command line arguments when running.\n
        python3 batchSchedulingComparison.py batchfile.txt ShortestRemaining""")
        return 1

    # Get the batch file name from the arguments
    batchfile_name = sys.argv[1]
    try:
        with open(batchfile_name, 'r') as f:
            batchfile_data = f.readlines()
            _, process_arrival_times, process_burst_times = parse_batchfile(batchfile_data)
    except FileNotFoundError:
        print("Input batchfile not found!")
        return 1

    # Get the sorting algorithm from the arguments and check if it is valid
    sorting_algorithm_name = sys.argv[2]
    if sorting_algorithm_name not in ["ShortestRemaining", "RoundRobin"]:
        print("Unidentified sorting algorithm. Please input either ShortestRemaining or RoundRobin.")
        return 1
    if sorting_algorithm_name == "ShortestRemaining":
        process_completion_times, sorted_pids = shortest_remaining(processes)
    elif sorting_algorithm_name == "RoundRobin":
        process_completion_times, sorted_pids = round_robin(processes)

    # Compute algorithm stats and print them
    avg_turnaround_time, avg_wait_time, process_turnaround_times, process_wait_times = compute_stats(process_completion_times, process_arrival_times, process_burst_times)
    print("PID ORDER OF EXECUTION:\n")
    for pid in sorted_pids:
        print(pid)

    print("\nAverage Process Turnaround Time: ", avg_turnaround_time)
    print("Average Process Wait Time: ", avg_wait_time)


# Sorting algorithm functions
def shortest_remaining(processes):
    process_completion_times, sorted_pids = [], []
    process_objects = []
    hq.heapify(process_objects)
    current_time = 0
    for i in range(len(processes) - 1):
        if i == 0 or processes[i][1] == processes[i - 1][1]:
            pid, arrival_time, burst_time = processes[i]
            hq.heappush(process_objects, Process(pid, arrival_time, burst_time))
            continue
        for j in range(len(process_objects) - 1):
            time_until_process_end = process_objects[j].burst_time
            if j != len(process_objects) - 1:
                time_until_new_arrival = process_objects[j + 1].arrival_time - current_time
                if time_until_process_end > time_until_new_arrival:
                    process_objects[j].burst_time -= time_until_new_arrival
                    current_time += time_until_new_arrival
                    hq.heappush(process_objects, process_objects[j + 1])
                    break
            current_time += time_until_process_end
            sorted_pids.append((process_objects.pop()).pid)
            process_completion_times.append(current_time)
    return process_completion_times, sorted_pids


def RoundRobinSort(processes):
    sorted_pids, request_queue, add_end = [], [], []
    processes, times = {k:v for (k, v) in processes}, {}
    time_quanta = 10
    current_time = 0

    while len(processes) != 0:
        for pid, [arrival, _] in processes.items():
            if arrival <= current_time and pid not in request_queue and pid not in add_end:
                request_queue.append(pid)

        request_queue.extend(add_end)
        add_end = []

        for i in range(len(request_queue)):
            currentProcess = request_queue.pop(0)
            bTime = processes[currentProcess][1]
            current_time += time_quanta if bTime >= time_quanta else bTime
            processes[currentProcess][1] -= time_quanta

            if processes[currentProcess][1] <= 0:
                processes.pop(currentProcess)
            else:
                add_end.append(currentProcess)

            sorted_pids.append(currentProcess)
            times[currentProcess] = current_time

    process_completion_times = list(times.values())
    return process_completion_times, sorted_pids

# Compute Stats function
def compute_stats(process_completion_times, process_arrival_times, process_burst_times):
    process_turnaround_times, process_wait_times = [], []
    for completion_time, arrival_time, burst_time in zip(process_completion_times, process_arrival_times, process_burst_times):
        # Turnaround time = Completion time - Arrival time
        turnaround_time = completion_time - arrival_time
        process_turnaround_times.append(turnaround_time)
        # Waiting time = Turnaround time - Burst time
        process_wait_times.append(turnaround_time - burst_time)
    avg_turnaround_time = sum(process_turnaround_times) / len(process_completion_times)
    avg_wait_time = sum(process_wait_times) / len(process_completion_times)
    return avg_turnaround_time, avg_wait_time, process_turnaround_times, process_wait_times


if __name__ == '__main__':
    main()


# Completion Time -> Time when the process completes its execution
# Turnaround Time -> Completion time - Arrival time
# Waiting Time -> Turnaround time - Burst time
# Response Time -> First CPU burst - Arrival time
