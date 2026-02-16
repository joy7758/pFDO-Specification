use criterion::{black_box, criterion_group, criterion_main, Criterion};
use blake3;
use sha2::{Sha256, Digest};

fn bench_algorithms(c: &mut Criterion) {
    let data = vec![0u8; 1024 * 1024]; // 模拟 1MB 数据块
    let mut group = c.benchmark_group("Sovereign_1.6T_Simulation");

    group.bench_function("BLAKE3_Sovereign_Gate", |b| {
        b.iter(|| blake3::hash(black_box(&data)))
    });

    group.bench_function("SHA256_Traditional_Gate", |b| {
        b.iter(|| {
            let mut hasher = Sha256::new();
            hasher.update(black_box(&data));
            hasher.finalize()
        })
    });

    group.finish();
}

criterion_group!(benches, bench_algorithms);
criterion_main!(benches);
