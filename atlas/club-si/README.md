# AtlasClub Campus (`club.atlas-si.com`) — Pacote de Produção & Centralização

Este diretório prepara o **AtlasClub** (baseado em **LearnHouse**, licença **AGPL-3.0** preservada integralmente na raiz) para operar como a **Casa Única Comercial** em **`https://club.atlas-si.com`**.

## Estrutura de Ofertas (Free + Pago em 1 Único Campus)

Em vez de manter múltiplos sites isolados, todas as ofertas vivem sob o mesmo registo de membro em `club.atlas-si.com`, segmentadas por **Comunidades** e **UserGroups**:

| Código Oferta (`pay.atlashub.si`) | UserGroup LearnHouse | Acesso | Descrição |
|---|---|---|---|
| `club_free_pt` | `club-free-pt` | **Free** | Comunidade Free · Genesis (Português) |
| `club_free_fr` | `club-free-fr` | **Free** | Comunidade Free · France (Français) |
| `club_premium` | `club-premium` | **Pago** | Comunidade Premium + Biblioteca + Calls |
| `course_atlas_harness` | `courses-pro` | **Pago** | Cursos Pagos · Formação Atlas-Harness |
| `mentorship_vip` | `mentorship-vip` | **Pago** | Mentorias Pagas · Executivos & Implementação |
| `projects_lab` | `projects-lab` | **Pago / B2B** | Projetos & Atlas Lab (Turmas e Clientes) |

## Integração com o Ecossistema Atlas

- **Matrículas Automáticas (`pay.atlashub.si`):** Toda compra ou cancelamento na **Hotmart**, **Whop.com**, **Checkout Direto** ou **CRM (`crm.atlashub.si`)** provisiona/revoga automaticamente o membro no UserGroup correspondente via API REST (`/api/v1/`).
- **Antena ao Vivo (`radar.atlas-si.com`):** Pode ser referenciada ou embutida como recurso externo dentro das comunidades Free e Premium para retenção diária.

## Como subir na VPS

1. Copie `.env.club.atlas-si.com.example` para `.env` e preencha senhas/chaves reais.
2. Suba o stack:
   ```bash
   docker compose --env-file .env -f docker-compose.club.yml up -d --build
   ```
3. Configure o proxy Caddy com `Caddyfile.club.atlas-si.com`.
4. Rode o bootstrap de UserGroups para gerar os IDs reais e atualizar `offers.json` no `AtlasPayBridge`:
   ```bash
   python3 seed_campus.py --api-url https://club.atlas-si.com/api/v1 --email admin@atlashub.si --password "SUA_SENHA"
   ```
