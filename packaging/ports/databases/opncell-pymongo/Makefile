PORTNAME=       opncell-pymongo
DISTVERSION=    4.18.2
CATEGORIES=     databases python
MASTER_SITES=   https://files.pythonhosted.org/packages/source/p/pymongo/
DISTNAME=       pymongo-${DISTVERSION}

MAINTAINER=     support@ds.co.ug
COMMENT=        Private pure-Python MongoDB client for OPNcell local reads
WWW=            https://www.mongodb.com/docs/languages/python/pymongo-driver/current/
LICENSE=        APACHE20
LICENSE_FILE=   ${WRKSRC}/LICENSE
RUN_DEPENDS=    python313>=3.13:lang/python313
ACTUAL-PACKAGE-DEPENDS= ${SH} ${FILESDIR}/package-dependencies.sh
NO_BUILD=       yes
NO_ARCH=        yes

# A private module path avoids shadowing OPNsense modules or owning shared CLIs.
# C extensions are optional upstream. The local IP connection needs no DNS/SRV extras.
do-install:
	${MKDIR} ${STAGEDIR}${DATADIR}
	cd ${WRKSRC} && ${COPYTREE_SHARE} "bson pymongo gridfs" ${STAGEDIR}${DATADIR}
	${FIND} ${STAGEDIR}${DATADIR} -type f ! \( -name '*.py' -o -name '*.pyi' -o -name 'py.typed' \) -delete
	${INSTALL_DATA} ${WRKSRC}/LICENSE ${WRKSRC}/THIRD-PARTY-NOTICES ${STAGEDIR}${DATADIR}/
	${FIND} ${STAGEDIR}${DATADIR} -type f | ${SORT} | ${SED} 's|^${STAGEDIR}${PREFIX}/||' >> ${TMPPLIST}

.include <bsd.port.mk>
