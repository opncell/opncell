PORTNAME=	opncell-mongosh
DISTVERSION=	2.14.0
CATEGORIES=	databases
DISTFILES=	${DISTNAME}.tar.gz

MAINTAINER=	support@ds.co.ug
COMMENT=	MongoDB Shell for OPNcell subscriber provisioning
WWW=		https://github.com/mongodb-js/mongosh

RUN_DEPENDS=	node22>0:www/node22
NO_BUILD=	yes

do-install:
	cd ${WRKSRC} && ${COPYTREE_SHARE} . ${STAGEDIR}${DATADIR}
	${INSTALL_SCRIPT} ${FILESDIR}/mongosh ${STAGEDIR}${PREFIX}/bin/mongosh
	${FIND} ${STAGEDIR}${DATADIR} \( -type f -o -type l \) | ${SORT} | \
	    ${SED} 's|^${STAGEDIR}${PREFIX}/||' >> ${TMPPLIST}

PLIST_FILES=	bin/mongosh

.include <bsd.port.mk>
