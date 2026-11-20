# Reverse proxy Caddy para AtlasClub (club.atlas-si.com)
# Nota: /api/auth/* e /api/revalidate pertencem ao Next.js (3010);
# apenas /api/v1* e /content* vão para o backend FastAPI (1348).

club.atlas-si.com {
	encode gzip

	handle /api/v1* {
		reverse_proxy 127.0.0.1:1348
	}
	handle /content* {
		reverse_proxy 127.0.0.1:1348
	}
	handle /collab* {
		reverse_proxy 127.0.0.1:4000
	}
	handle {
		reverse_proxy 127.0.0.1:3010
	}
}
