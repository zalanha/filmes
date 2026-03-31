package com.unilopers.cinema.service.async;

import com.unilopers.cinema.model.Sala;
import com.unilopers.cinema.model.Sessao;
import com.unilopers.cinema.repository.SalaRepository;
import com.unilopers.cinema.repository.SessaoRepository;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.util.List;

@Service
public class SalaSchedulerService {

    private static final Logger logger = LoggerFactory.getLogger(SalaSchedulerService.class);

    @Autowired
    private SalaRepository salaRepository;

    @Autowired
    private SessaoRepository sessaoRepository;

    /**
     * Nicholas Gabriel: Atualização automática de disponibilidade de Sala.
     * Roda a cada 1 minuto (cron = "0 * * * * *").
     */
    @Scheduled(cron = "0 * * * * *")
    @Transactional
    public void verificarOcupacaoDasSalas() {
        logger.info("[CRON-SALA] Iniciando ciclo de verificação de disponibilidade...");
        
        LocalDateTime agora = LocalDateTime.now();
        List<Sala> todasAsSalas = salaRepository.findAll();
        List<Sessao> sessoesAtivas = sessaoRepository.findAll();

        for (Sala sala : todasAsSalas) {
            boolean estaOcupadaAgora = false;
            String filmeAtual = "";

            for (Sessao sessao : sessoesAtivas) {
                // Blindagem contra dados incompletos
                if (sessao.getSala() == null || sessao.getFilme() == null || sessao.getDataHora() == null) {
                    continue;
                }

                if (sessao.getSala().getId().equals(sala.getId())) {
                    LocalDateTime inicio = sessao.getDataHora();
                    Integer duracao = sessao.getFilme().getDuracaoMin();
                    if (duracao == null) duracao = 120; // Padrão 2 horas

                    LocalDateTime fim = inicio.plusMinutes(duracao);

                    if (agora.isAfter(inicio) && agora.isBefore(fim)) {
                        estaOcupadaAgora = true;
                        filmeAtual = sessao.getFilme().getTitulo();
                        break;
                    }
                }
            }

            // Otimização: Só grava no banco se o status mudou
            // Se estaOcupadaAgora for true, entao disponivel deve ser false
            boolean novoStatusDisponivel = !estaOcupadaAgora;
            
            // Tratamento para evitar NullPointer no campo da entidade
            boolean statusAtual = (sala.getDisponivel() != null) ? sala.getDisponivel() : true;

            if (statusAtual != novoStatusDisponivel) {
                sala.setDisponivel(novoStatusDisponivel);
                salaRepository.save(sala);
                
                if (estaOcupadaAgora) {
                    logger.info("[CRON-SALA] Sala '{}' Ocupada (Filme: '{}')", sala.getNome(), filmeAtual);
                } else {
                    logger.info("[CRON-SALA] Sala '{}' Liberada (Disponível)", sala.getNome());
                }
            }
        }
        
        logger.info("[CRON-SALA] Ciclo de verificação finalizado.");
    }
}
