-- phpMyAdmin SQL Dump
-- version 5.2.0
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Waktu pembuatan: 01 Bulan Mei 2024 pada 08.46
-- Versi server: 10.4.27-MariaDB
-- Versi PHP: 8.2.0

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `aes_umpo`
--

-- --------------------------------------------------------

--
-- Struktur dari tabel `dosen_matkul`
--

CREATE TABLE `dosen_matkul` (
  `id_dosen` int(11) NOT NULL,
  `id_matkul` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;

-- --------------------------------------------------------

--
-- Struktur dari tabel `jawaban`
--

CREATE TABLE `jawaban` (
  `id_jawaban` int(11) NOT NULL,
  `id_soal` int(11) NOT NULL,
  `id_mahasiswa` int(11) NOT NULL,
  `jawaban` text NOT NULL,
  `nilai_jawaban` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;

-- --------------------------------------------------------

--
-- Struktur dari tabel `kuis`
--

CREATE TABLE `kuis` (
  `id_kuis` int(11) NOT NULL,
  `kuis_ke` varchar(3) NOT NULL,
  `id_matkul` int(11) NOT NULL,
  `deadline` datetime NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;

-- --------------------------------------------------------

--
-- Struktur dari tabel `mahasiswa_kuis`
--

CREATE TABLE `mahasiswa_kuis` (
  `id_mahasiswa` int(11) NOT NULL,
  `id_kuis` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;

-- --------------------------------------------------------

--
-- Struktur dari tabel `matkul`
--

CREATE TABLE `matkul` (
  `id_matkul` int(11) NOT NULL,
  `kode_matkul` varchar(20) NOT NULL,
  `nama_matkul` varchar(50) NOT NULL,
  `tahun_ajaran` varchar(15) NOT NULL,
  `id_dosen` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;

-- --------------------------------------------------------

--
-- Struktur dari tabel `soal`
--

CREATE TABLE `soal` (
  `id_soal` int(11) NOT NULL,
  `soal` text NOT NULL,
  `jawaban_kunci` text NOT NULL,
  `bobot_nilai` int(11) NOT NULL,
  `id_kuis` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;

-- --------------------------------------------------------

--
-- Struktur dari tabel `user`
--

CREATE TABLE `user` (
  `id_user` int(11) NOT NULL,
  `no_induk` varchar(20) NOT NULL,
  `nama` varchar(100) NOT NULL,
  `password` varchar(200) NOT NULL,
  `role` int(1) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;

--
-- Dumping data untuk tabel `user`
--

INSERT INTO `user` (`id_user`, `no_induk`, `nama`, `password`, `role`) VALUES
(1, '20533243', 'Ghauzar Andhika Akbar', 'b\'gAAAAABmJ8d0RErJpLWwH3hPkKpQDxljcaaFR7vJNGWILTAtagFeI-7PnUyb119P9LrCtBnc2xjDsa1xke-M3Goru1P_Pk826Q==\'', 1);

--
-- Indexes for dumped tables
--

--
-- Indeks untuk tabel `dosen_matkul`
--
ALTER TABLE `dosen_matkul`
  ADD KEY `id_dosen` (`id_dosen`),
  ADD KEY `id_matkul` (`id_matkul`);

--
-- Indeks untuk tabel `jawaban`
--
ALTER TABLE `jawaban`
  ADD PRIMARY KEY (`id_jawaban`),
  ADD KEY `id_mahasiswa` (`id_mahasiswa`),
  ADD KEY `id_soal` (`id_soal`);

--
-- Indeks untuk tabel `kuis`
--
ALTER TABLE `kuis`
  ADD PRIMARY KEY (`id_kuis`),
  ADD KEY `id_matkul` (`id_matkul`);

--
-- Indeks untuk tabel `mahasiswa_kuis`
--
ALTER TABLE `mahasiswa_kuis`
  ADD KEY `id_mahasiswa` (`id_mahasiswa`),
  ADD KEY `id_kuis` (`id_kuis`);

--
-- Indeks untuk tabel `matkul`
--
ALTER TABLE `matkul`
  ADD PRIMARY KEY (`id_matkul`),
  ADD KEY `id_dosen` (`id_dosen`);

--
-- Indeks untuk tabel `soal`
--
ALTER TABLE `soal`
  ADD PRIMARY KEY (`id_soal`),
  ADD KEY `id_kuis` (`id_kuis`);

--
-- Indeks untuk tabel `user`
--
ALTER TABLE `user`
  ADD PRIMARY KEY (`id_user`);

--
-- AUTO_INCREMENT untuk tabel yang dibuang
--

--
-- AUTO_INCREMENT untuk tabel `jawaban`
--
ALTER TABLE `jawaban`
  MODIFY `id_jawaban` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT untuk tabel `kuis`
--
ALTER TABLE `kuis`
  MODIFY `id_kuis` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT untuk tabel `matkul`
--
ALTER TABLE `matkul`
  MODIFY `id_matkul` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT untuk tabel `soal`
--
ALTER TABLE `soal`
  MODIFY `id_soal` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT untuk tabel `user`
--
ALTER TABLE `user`
  MODIFY `id_user` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- Ketidakleluasaan untuk tabel pelimpahan (Dumped Tables)
--

--
-- Ketidakleluasaan untuk tabel `dosen_matkul`
--
ALTER TABLE `dosen_matkul`
  ADD CONSTRAINT `dosen_matkul_ibfk_1` FOREIGN KEY (`id_dosen`) REFERENCES `user` (`id_user`),
  ADD CONSTRAINT `dosen_matkul_ibfk_2` FOREIGN KEY (`id_matkul`) REFERENCES `matkul` (`id_matkul`);

--
-- Ketidakleluasaan untuk tabel `jawaban`
--
ALTER TABLE `jawaban`
  ADD CONSTRAINT `jawaban_ibfk_1` FOREIGN KEY (`id_mahasiswa`) REFERENCES `user` (`id_user`),
  ADD CONSTRAINT `jawaban_ibfk_2` FOREIGN KEY (`id_soal`) REFERENCES `soal` (`id_soal`);

--
-- Ketidakleluasaan untuk tabel `kuis`
--
ALTER TABLE `kuis`
  ADD CONSTRAINT `kuis_ibfk_1` FOREIGN KEY (`id_matkul`) REFERENCES `matkul` (`id_matkul`);

--
-- Ketidakleluasaan untuk tabel `mahasiswa_kuis`
--
ALTER TABLE `mahasiswa_kuis`
  ADD CONSTRAINT `mahasiswa_kuis_ibfk_1` FOREIGN KEY (`id_mahasiswa`) REFERENCES `user` (`id_user`),
  ADD CONSTRAINT `mahasiswa_kuis_ibfk_2` FOREIGN KEY (`id_kuis`) REFERENCES `kuis` (`id_kuis`);

--
-- Ketidakleluasaan untuk tabel `matkul`
--
ALTER TABLE `matkul`
  ADD CONSTRAINT `matkul_ibfk_1` FOREIGN KEY (`id_dosen`) REFERENCES `user` (`id_user`);

--
-- Ketidakleluasaan untuk tabel `soal`
--
ALTER TABLE `soal`
  ADD CONSTRAINT `soal_ibfk_1` FOREIGN KEY (`id_kuis`) REFERENCES `kuis` (`id_kuis`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
