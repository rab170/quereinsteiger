CREATE TABLE "overview" ( 
      "area" INTEGER, 
      "borough" TEXT, 
      "frei_ab" TEXT, 
      "price" INTEGER, 
      "url" TEXT UNIQUE ON CONFLICT REPLACE, 
      "wohnung_typ" TEXT, 
      "price_area_ratio" REAL, 
      "created" TIMESTAMP DEFAULT (DATETIME('now'))
);
