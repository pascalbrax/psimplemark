import timeit
import multiprocessing
import platform
import time

# Define the number of operations
NUM_OPERATIONS = 10**7  # 10 million operations per core

# Updated reference benchmark results (FLOPS in 10 seconds)
REFERENCE_RESULTS = {
    "Linux - Intel Celeron J6412 @ 2.00GHz": 185204087160836,
    "Windows - Intel Xeon E3-1240 v5 @ 3.50GHz": 296326539457337,
    "Linux - Intel Xeon E-2246G @ 3.60GHz": 777857166075511,
    "Linux - Intel Xeon E5-2643 @ 3.30GHz (2 Sockets)": 657474509420968,
    "Linux - Intel Xeon E-2314 @ 2.80GHz": 527831648408383,
    "Linux - Intel Xeon E5-2650 v3 @ 2.30GHz (1 core)": 64821430506292,
    "Linux - Intel Xeon E5-2650 v4 @ 2.20GHz": 1361250040632145,
    "Linux - Intel Xeon E5-2630 0 @ 2.30GHz": 351887765605588,
    "Linux - Raspberry RPi 4 Model B @ 1.50GHz": 111122452296501,
}

def get_processor_name():
    """Retrieves the CPU name cross-platform without external libraries."""
    cpu_name = platform.processor()

    if not cpu_name:  # Empty on some Linux systems
        try:
            with open("/proc/cpuinfo", "r") as f:
                for line in f:
                    if "model name" in line:
                        return line.strip().split(":")[1].strip()
        except FileNotFoundError:
            return "Unknown CPU"

    return cpu_name

def floating_point_throughput(_=None):
    """Measures how many floating-point operations can be executed in 10 seconds."""
    count = 0
    start_time = time.time()
    while time.time() - start_time < 10:
        count += sum((i * 0.5) / (i % 7 + 1) for i in range(1, NUM_OPERATIONS))
    return count

def floating_point_single_core():
    """Runs floating-point test on a single core for 10 seconds."""
    return floating_point_throughput()

def convert_to_flops_units(value):
    """Converts a FLOPS value to a human-readable format (GFLOPS, TFLOPS)."""
    if value >= 1e12:
        return f"{value / 1e12:.2f} TFLOPS"
    elif value >= 1e9:
        return f"{value / 1e9:.2f} GFLOPS"
    else:
        return f"{value:.0f} FLOPS"

def truncate_name(name, max_length=55):
    """Truncates system name if it exceeds max_length."""
    return name if len(name) <= max_length else name[:max_length - 3] + "..."

def print_flops_comparison(current_flops):
    """Prints a sorted comparison of the current system against reference CPU benchmarks, including itself."""
    print("\n=== FLOPS COMPARISON ===")

    # Get system name and truncate if necessary
    system_name = f"{platform.system()} - {get_processor_name()}"
    system_name = truncate_name(system_name)

    # Add current system to comparison list
    all_results = {**REFERENCE_RESULTS, system_name: current_flops}

    # Sort by FLOPS in descending order
    sorted_results = sorted(all_results.items(), key=lambda x: x[1], reverse=True)

    max_reference = sorted_results[0][1]  # Best known CPU performance
    bar_length = 20  # Max bar width

    for system, ref_flops in sorted_results:
        system = truncate_name(system)  # Ensure all names fit the table
        normalized_length = int((ref_flops / max_reference) * bar_length)
        bar_char = "▒"  # Darker gray for reference systems
        if system == system_name:
            bar_char = "█"  # Full white for current system

        bar = bar_char * normalized_length
        ref_flops_human = convert_to_flops_units(ref_flops)

        if system == system_name:
            print(f"{system.ljust(55)} [{bar.ljust(bar_length)}] {ref_flops_human} <-- YOU")
        else:
            print(f"{system.ljust(55)} [{bar.ljust(bar_length)}] {ref_flops_human}")

def run_benchmark():
    print(f"\n=== CPU BENCHMARK REPORT ===")
    print(f"System: {platform.system()} - {get_processor_name()}")
    print(f"CPU Cores: {multiprocessing.cpu_count()}\n")

    print("\n>>> Running Single-Core Floating-Point Test (10s)...")
    single_core_flops = floating_point_single_core()
    single_core_flops_per_sec = single_core_flops / 10
    single_core_flops_human = convert_to_flops_units(single_core_flops_per_sec)

    print(f"Single-Core Floating-Point Operations in 10 seconds: {single_core_flops:,}")
    print(f"Approximate Single-Core Performance: {single_core_flops_human}")

    print("\n>>> Running Multi-Core Floating-Point Test (10s)...")
    num_cores = multiprocessing.cpu_count()
    with multiprocessing.Pool(processes=num_cores) as pool:
        results = pool.map(floating_point_throughput, [None] * num_cores)
    total_flops = sum(results)

    flops_per_sec = total_flops / 10  # FLOPS (Floating-Point Operations Per Second)
    flops_human_readable = convert_to_flops_units(flops_per_sec)

    print(f"Multi-Core Floating-Point Operations in 10 seconds: {total_flops:,}")
    print(f"Approximate Multi-Core Performance: {flops_human_readable}")

    # Print sorted comparison including our system
    print_flops_comparison(total_flops)

if __name__ == "__main__":
    run_benchmark()
