# 
# Bases de Dados 2021/2022
# Trabalho Prático
#
# Authors: 
#   Nuno Antunes <nmsa@dei.uc.pt>
#   BD 2022 Team - https://dei.uc.pt/lei/
#   University of Coimbra

FROM library/postgres


ENV POSTGRES_USER grupox
ENV POSTGRES_PASSWORD grupox
ENV POSTGRES_DB market_place

COPY market_place.sql /docker-entrypoint-initdb.d/

EXPOSE 5432
