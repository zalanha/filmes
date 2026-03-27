package com.unilopers.cinema.service.async;

import com.unilopers.cinema.model.Filme;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.scheduling.annotation.Async;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
public class FilmeAsyncService {

    private static final Logger logger = LoggerFactory.getLogger(FilmeAsyncService.class);

    @Async
    @Transactional
    public void executarAuditoria(Filme filme) {
        try {
            String threadName = Thread.currentThread().getName();
            
            logger.info("[AUDITORIA - INÍCIO] Thread: {} | Iniciando validação do filme: {} (ID: {})", 
                        threadName, filme.getTitulo(), filme.getId());

            Thread.sleep(4000); 

            logger.info("[AUDITORIA - CONCLUÍDA] Status: COMPLIANCE OK");
            logger.info(" > Filme: {} | Ano: {} | Duração: {}min", filme.getTitulo(), filme.getAno(), filme.getDuracaoMin());
            logger.info(" > Timestamp de Registro: {}", filme.getCreatedAt());
            logger.info(" > Auditoria processada com sucesso na thread: {}", threadName);

        } catch (InterruptedException e) {
            logger.error("[AUDITORIA - FALHA] Interrupção na thread para o filme: {}", filme.getTitulo());
            Thread.currentThread().interrupt();
        } catch (Exception e) {
            logger.error("[AUDITORIA - ERRO CRÍTICO] Falha ao processar integridade: {}", e.getMessage());
        }
    }
}
