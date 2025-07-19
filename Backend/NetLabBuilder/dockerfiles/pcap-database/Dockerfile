FROM mysql:8.0

# Set environment variables
ENV MYSQL_ROOT_PASSWORD=pcap_root_password
ENV MYSQL_DATABASE=pcap_db
ENV MYSQL_USER=pcap_user
ENV MYSQL_PASSWORD=pcap_user_password

# Copy initialization script
COPY init.sql /docker-entrypoint-initdb.d/

# Create directory for PCAP file storage
RUN mkdir -p /pcap_storage && \
    chown -R mysql:mysql /pcap_storage

# Copy MySQL configuration
COPY my.cnf /etc/mysql/conf.d/my.cnf

# Expose MySQL port
EXPOSE 3306

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD mysqladmin ping -h localhost -u root -p${MYSQL_ROOT_PASSWORD} || exit 1 