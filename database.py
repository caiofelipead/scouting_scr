    def get_buscas_salvas(self, criado_por=None):
        """Recupera buscas salvas do banco de dados"""
        try:
            if criado_por:
                query = """
                SELECT id_busca, nome_busca, filtros, criado_por, criado_em
                FROM buscas_salvas
                WHERE criado_por = :usuario
                ORDER BY criado_em DESC
                """
                params = {'usuario': criado_por}
            else:
                query = """
                SELECT id_busca, nome_busca, filtros, criado_por, criado_em
                FROM buscas_salvas
                ORDER BY criado_em DESC
                """
                params = {}
            
            return pd.read_sql(text(query), self.engine, params=params)
        except Exception as e:
            print(f"❌ Erro ao buscar buscas salvas: {e}")
            return pd.DataFrame()

    def salvar_busca(self, nome_busca: str, filtros: dict, criado_por: str = None) -> bool:
        """Salva uma busca personalizada"""
        try:
            filtros_json = json.dumps(filtros)
            
            with self.engine.connect() as conn:
                conn.execute(text("""
                    INSERT INTO buscas_salvas (nome_busca, filtros, criado_por)
                    VALUES (:nome, :filtros, :usuario)
                """), {
                    'nome': nome_busca,
                    'filtros': filtros_json,
                    'usuario': criado_por
                })
                conn.commit()
            
            return True
        except Exception as e:
            print(f"❌ Erro ao salvar busca: {e}")
            return False

    def deletar_busca_salva(self, id_busca: int) -> bool:
        """Remove uma busca salva"""
        try:
            with self.engine.connect() as conn:
                conn.execute(text("DELETE FROM buscas_salvas WHERE id_busca = :id"), 
                            {'id': self._safe_int(id_busca)})
                conn.commit()
            return True
        except Exception as e:
            print(f"❌ Erro ao deletar busca: {e}")
            return False

    def carregar_filtros_busca(self, id_busca: int) -> Optional[dict]:
        """Carrega os filtros de uma busca salva"""
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text("""
                    SELECT filtros FROM buscas_salvas WHERE id_busca = :id
                """), {'id': self._safe_int(id_busca)}).fetchone()
                
                if result:
                    return json.loads(result[0])
                return None
        except Exception as e:
            print(f"❌ Erro ao carregar filtros: {e}")
            return None
