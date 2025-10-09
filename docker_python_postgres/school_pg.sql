DROP TABLE IF EXISTS "c_regel" CASCADE;
DROP TABLE IF EXISTS "cursist" CASCADE;
DROP TABLE IF EXISTS "cursus" CASCADE;
DROP TABLE IF EXISTS "docent" CASCADE;

CREATE TABLE cursist (
    cursistnr VARCHAR(4) PRIMARY KEY,
    naam VARCHAR(25),
    roepnaam VARCHAR(25),
    straat VARCHAR(25),
    postcode VARCHAR(7),
    plaats VARCHAR(25),
    geslacht VARCHAR(1),
    geb_datum DATE
);

--
-- Gegevens worden geëxporteerd voor tabel 'cursist'
--
INSERT INTO cursist (cursistnr, naam, roepnaam, straat, postcode, plaats, geslacht, geb_datum) VALUES
('64', 'Broeken', 'Bram', 'Drimmelseweg 8', '4395 XX', 'Made', 'M', '1988-03-24'),
('88', 'Vos', 'Henk', 'Besbeemd 64', '4142 CE', 'Oosterhout', 'M', '1989-09-22'),
('2', 'Krimpen', 'Tanja', 'Tilburgseweg 2', '4222 BB', 'Goirle', 'V', '1990-02-08'),
('14', 'Norbart', 'Niels', 'Gershof 8', '4841 PL', 'Breda', 'M', '1987-12-06');

-- --------------------------------------------------------

--
-- Tabelstructuur voor tabel 'cursus'
--
CREATE TABLE cursus (
    curs_code VARCHAR(8) PRIMARY KEY,
    curs_plts VARCHAR(25),
    curs_dat DATE,
    omschr VARCHAR(25),
    doc_code VARCHAR(2),
    curs_prijs DECIMAL(6,2)
);

--
-- Gegevens worden geëxporteerd voor tabel 'cursus'
--
INSERT INTO cursus (curs_code, curs_plts, curs_dat, omschr, doc_code, curs_prijs) VALUES
('DB3', 'Breda', '1993-12-04', 'Dbase III Plus', 'WI', 3300.00),
('DB4', 'Etten', '1993-12-11', 'Dbase IV', 'HM', 3600.00),
('OA2', 'Made', '1993-11-13', 'Open Access 2.1', 'PE', 2400.00),
('OA3', 'Breda', '1993-11-13', 'Open Access 3.0', 'GR', 2600.00),
('FW', 'Breda', '1993-11-20', 'Framework', 'WI', 850.00),
('WP', 'Breda', '1993-11-20', 'Wordperfect', 'GR', 1450.00),
('NO', 'Breda', '1993-12-06', 'Normaliseren', 'MO', 3000.00),
('C++', 'Made', '1993-11-27', 'Programmeren in C++', 'MO', 1450.00);

-- --------------------------------------------------------

--
-- Tabelstructuur voor tabel 'c_regel'
--
CREATE TABLE c_regel (
    curs_code VARCHAR(8),
    cursistnr VARCHAR(4),
    cijfer DECIMAL(2,0),
    betaald DECIMAL(6,2)
);



--
-- Gegevens worden geëxporteerd voor tabel 'c_regel'
--
INSERT INTO c_regel (curs_code, cursistnr, cijfer, betaald) VALUES
('DB3', '64', 8, 3300.00),
('DB3', '2', 6, NULL),
('OA2', '14', 5, 2400.00),
('OA2', '88', 7, 2000.00),
('OA2', '2', 9, NULL),
('DB4', '14', 6, 3600.00);

-- --------------------------------------------------------

--
-- Tabelstructuur voor tabel 'docent'
--
CREATE TABLE docent (
    doc_code VARCHAR(2) PRIMARY KEY,
    doc_naam VARCHAR(25),
    straat VARCHAR(25),
    postcode VARCHAR(7),
    plaats VARCHAR(25),
    telefoon VARCHAR(12),
    uurloon DECIMAL(5,2),
    geb_datum DATE
);

--
-- Gegevens worden geëxporteerd voor tabel 'docent'
--
INSERT INTO docent (doc_code, doc_naam, straat, postcode, plaats, telefoon, uurloon, geb_datum) VALUES
('WI', 'Witlok', 'Madeseweg 8', '4841 PT', 'Oosterhout', '071-123378', 100.00, '1957-04-25'),
('HM', 'Hooymayers', 'Ignatiusstr 6', '4847 EZ', 'Breda', '076-442786', 200.00, '1952-09-01'),
('GR', 'Grond', 'Bolwerk 10', '4541 CC', 'Tilburg', '013-426786', 150.00, '1958-10-25'),
('PE', 'Peters', 'Breedonk 64', '4142 EC', 'Oosterhout', '01620-3429', 185.50, '1963-10-08'),
('SE', 'Sengers', 'Bredaseweg 2', '4344 DE', 'Bavel', NULL, 110.00, '1955-05-17'),
('MO', 'Mol', 'Waterstr 8', '4841 KA', 'Breda', '076-227788', 300.00, '1948-11-30');

--
-- Voeg een buitenlandse sleutel toe aan de 'cursus' tabel die verwijst naar 'docent'
-- Dit kon niet eerder omdat de 'docent' tabel nog niet bestond.
--
ALTER TABLE cursus ADD FOREIGN KEY (doc_code) REFERENCES docent(doc_code);
ALTER TABLE c_regel ADD PRIMARY KEY (curs_code, cursistnr);
ALTER TABLE c_regel ADD FOREIGN KEY (curs_code) REFERENCES cursus(curs_code);
ALTER TABLE c_regel ADD FOREIGN KEY (cursistnr) REFERENCES cursist(cursistnr);






