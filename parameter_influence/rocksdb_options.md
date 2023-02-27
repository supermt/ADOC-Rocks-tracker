# IO Options
- bytes_per_sync (**0** by default, turn off on default, smoothing the performance)
- Concurrency
  - max_open_files (**-1** by default, all files will be kept open)
  - max_file_opening_threads (**16** by default , configuring the *DB::Open()* use case)
- IO model
  - **Trigger Direct IO**
    - use_direct_io_for_flush_and_compaction
    - use_direct_reads (trigger the option *new_table_reader_for_compaction_inputs*)
    - use_direct_writes
  - Mmap (Linux)
    - allow_mmap_reads
    - allow_mmap_writes(**false** on default, disable the function *DB::SyncWAL()* )
  - Mmap (Windows)
    - writable_file_max_buffer_size (Dynamic changable, auto growing in buffered IO, fixed in direct IO )
    - random_access_max_buffer_size ()
  - is_fd_close_on_exec (disable child process inherit)
- Syscalls
  - allow_fallocate (true by default, bypass the fallocate syscall when false)
  - use_fsync (fdatasync or fsync, **false** by default)

- Access Model
  - *compaction_readahead_size* (0 by default, optimize for spinning disk, sequential operation than random access)
  - *access_hint_on_compaction_start* (**Normal** by default, can be set as NONE, NORMAL, SEQUENTIAL, WILLNEED)
  - *advise_random_on_open* (**true** by default, hint the underlying fs the file will be accessed by random)
- new_table_reader_for_compaction_inputs(**false** by default, delete on future, increase memory usage)
- avoid_unnecessary_blocking_io (use background threads to delete files, **false** by default, latency_sensitive options)
- preserve_deletes (**false** by default)
- About Write Thread Yield
  - enable_write_thread_adaptive_yield (**true** by default, improving the concurrency of write threads)
  - write_thread_slow_yield_usec (**3** by default)
  - write_thread_max_yield_usec (**100** by default)

- enable_pipelined_write (**false** by default, enable to improve write throughput and reduce two-phase commit latency)
- IO configuration for WAL
  - strict_bytes_per_sync (**false** by default, handle the cases where processing speed exceeds IO speed during file generation, causes the *huge sync* (I guess it may causes severe long tail latency). )
  - wal_bytes_per_sync
  - max_total_wal_size
  - manual_wal_flush
- delayed_write_rate (**0 or 16 MB** by default, adjusted by rate limiter)
- **special use cases**
  - unordered_write: higher throughput, the update of sequence number can't be guaranteed
  - 
# Memtable Options
- memtable_factory
- allow_concurrent_memtable_write
- db_write_buffer_size (**0** by default, size of Memtables acrosses all column families)
- write_buffer_size (**64 MB** by default, size of one single Memtable)
- write_buffer_manager (overrides the *db_write_buffer_size* options)
- *Memory Allocation*
  - memtable_huge_page_size
  - max_successive_merges
  - inpace_update_num_locks
- *Flush and Compaction*
  - min_write_buffer_number_to_merge
  - max_write_buffer_number_to_maintain
  - level0_stop_writes_trigger
  - level0_slowdown_writes_trigger
  - level0_file_num_compaction_trigger
  - max_write_buffer_size_to_maintain (deprecated)

# Cache Options
- table_cache_numshardbits
- pin_l0_filter_and_index_blocks_in_cache
- cache_index_and_filter_blocks_with_high_priority
- cache_index_and_filter_blocks

# Index Options
- *Bloom Filter Options*
  - bloom_locality
  - prefix_extractor
  - filter_policy
  - whole_key_filtering
  - data_block_hash_table_util_ratio
- pin_top_level_index_and_filter
- enable_index_compression
- *For Two Level Index options only*
  - metadata_block_size
  - partition_filters
  - index_block_restart_interval
- index_shortening
- data_block_index_type
- index_type
  
# WAL Settings
- WAL_ttl_seconds
- WAL_size_limit
- wal_dir
- atomic_flush (**false** by default, auto flushing the data or not)

# Compaction Configuration
- *compaction_pri* (**kMinOverlappingRatio** by default, optimize for lower WA)
- *compaction_style*(**Level** by default, can be universal, FIFO and None)
- periodic_compaction_seconds
- **Advanced Compaction Operator**
  - memtable_insert_with_hint_prefix_extractor
  - *compaction_filter*
  - comparator(**leveldb.BytewiseComparator** by default)
  - bottommost_compression (**disable** by default)
  - compaction_filter_factory
- *compaction_options_universal* (Options for universal compaction)
  - stop_style
  - compression_size_percent
  - allow_trivial_move
  - max_merge_width
  - max_size_amplification_percent
  - min_merge_width
  - size_ratio
- *compaction_options_fifo* (Options for FIFO compaction
  - allow_compaction
  - max_table_file_size
- num_levels
- target_file_size_multiplier
- hard_pending_compaction_bytes_limit (stops will be stopped if the compaction workload is too large)
- soft_pending_compaction_bytes_limit
- max_compaction_bytes (**target_file_size_base * 25** by default)
- level_compaction_dynamic_level_bytes


# SSTable Settings
- table_factory (**BlockBasedTable** by default)
- *compression*
- *Compaction related*
  - level_compaction_dynamic_level_bytes style
    - max_bytes_for_level_multiplier_additional(**useless** by default, only triggered by *level_compaction_dynamic_level_bytes*)
    - max_bytes_for_level_base
- *Read Options*
  - read_amp_bytes_per_bit
  - block_align
  - verify_compression
- *Block Format*
  - *block_size*
  - block_size_deviation (decide to close a block or not)
  - block_restart_interval (how many keys skipped before start a new run of delta compression)
- *Block IO*
  - no_block_cache
  - flush_block_policy_factory
- *Table Format*
  - checksum

# Iterator Settings
- max_seqential_skip_in_iterations

# Configuration of Thread Pool
- max_background_jobs (2 by default)
- base_background_compactions (decided by max_background_jobs)
- max_background_comapactions (abandoned)
- max_background_flushes
- use_adaptive_mutex
- max_subcompactions (**1** by default, decides how many subjobs generated from 1 compaction runs)
- max_background_jobs

# Other
- skip_stats_update_on_db_open
- manifest_preallocation_size (4MB by default)
- max_log_file_size (number of LOG file)
- create_if_missing
- enable_thread_tracking
- error_if_exists
- recycle_log_file_num
- skip_log_error_on_recovery
- LOG file configuration
  - db_log_dir
  - max_log_dir
  - manifest_preallocation_size
  - log_file_time_to_roll
  - keep_log_file_numparanoid_checks
- write_dbid_to_manifest
- avoid_flush_during_shutdown
- avoid_flush_during_recovery
- dump_malloc_states
- best_efforts_recoveryallow_2pc
- persist_stats_to_disk
- fail_if_options_file_error
- allow_ingest_behind
- paranoid_checks
- wal_recovery_mode
- allow_2pc
- report_bg_io_stats