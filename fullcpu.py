
import db_bench_option
import db_bench_runner

from db_bench_runner import reset_CPUs
from db_bench_runner import restrict_cpus
from db_bench_runner import initial_cgroup


initial_cgroup()
# restrict_cpus(12,1)
reset_CPUs()