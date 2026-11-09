PORTNAME=	open5gs
DISTVERSION=	2.8.0
CATEGORIES=	net

MAINTAINER=	ports@opncell.local
COMMENT=	Open5GS mobile core network
WWW=		https://open5gs.org/

LICENSE=	AGPLv3
LICENSE_FILE=	${WRKSRC}/LICENSE

USES=		bison localbase:ldflags meson ninja pkgconfig python:build ssl

BUILD_DEPENDS=	gsed:textproc/gsed

USE_GITHUB=	yes
GH_ACCOUNT=	open5gs
GH_PROJECT=	open5gs
GH_TAGNAME=	v${DISTVERSION}

LIB_DEPENDS=	\
		libbson-1.0.so:devel/libbson \
		libcurl.so:ftp/curl \
		libgnutls.so:security/gnutls \
		libidn.so:dns/libidn \
		libmicrohttpd.so:www/libmicrohttpd \
		libmongoc-1.0.so:devel/mongo-c-driver \
		libnghttp2.so:www/libnghttp2 \
		libtalloc.so:devel/talloc \
		libyaml.so:textproc/libyaml

USE_RC_SUBR=	open5gs_amf \
		open5gs_ausf \
		open5gs_bsf \
		open5gs_hss \
		open5gs_mme \
		open5gs_nrf \
		open5gs_nssf \
		open5gs_pcf \
		open5gs_pcrf \
		open5gs_scp \
		open5gs_sepp1 \
		open5gs_sepp2 \
		open5gs_sgwc \
		open5gs_sgwu \
		open5gs_smf \
		open5gs_udm \
		open5gs_udr \
		open5gs_upf

PORTREVISION= 1

post-configure:
	${PATCH} -d ${WRKSRC} -p1 < ${FILESDIR}/freeDiameter-basename.diff

.include <bsd.port.mk>
