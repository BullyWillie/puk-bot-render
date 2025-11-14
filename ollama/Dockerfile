FROM ollama/ollama:latest

USER root
RUN apt-get update && apt-get install -y curl
USER ollama

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]